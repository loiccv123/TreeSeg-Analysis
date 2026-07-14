import numpy as np
import pandas as pd
import open3d as o3d
import laspy
from pathlib import Path
import time
import sys

class TreeAligner:
    def __init__(
        self,
        out_dir: str,
        icp_voxel: float = 0.05,
        icp_fine_corr: float = 0.20,
        icp_coarse_corr: float = 2.0,
        icp_max_iters: int = 100,
    ):
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        
        self.icp_voxel = icp_voxel
        self.icp_fine_corr = icp_fine_corr
        self.icp_coarse_corr = icp_coarse_corr
        self.icp_max_iters = icp_max_iters

    @staticmethod
    def _read_laz(path: Path):
        """Reads a .las or .laz file and returns the coordinates and header."""
        las = laspy.read(str(path))
        pts = np.column_stack((las.x, las.y, las.z))
        return pts, las.header

    @staticmethod
    def _export_laz(points: np.ndarray, source_header, out_path: Path):
        """Exports the aligned points to a new .laz file using the original header offsets/scales."""
        new_header = laspy.LasHeader(point_format=3, version="1.2")
        new_header.offsets = source_header.offsets
        new_header.scales = source_header.scales

        las_out = laspy.LasData(new_header)
        las_out.x = points[:, 0]
        las_out.y = points[:, 1]
        las_out.z = points[:, 2]
        
        las_out.write(str(out_path))

    @staticmethod
    def _to_o3d(xyz: np.ndarray) -> o3d.geometry.PointCloud:
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(np.asarray(xyz, dtype=np.float64))
        return pcd

    def _icp_align_moving_to_base(self, pts_base: np.ndarray, pts_moving: np.ndarray):
        """Aligns pts_moving to fit pts_base."""
        if pts_base.shape[0] < 50 or pts_moving.shape[0] < 50:
            return pts_moving, np.eye(4, dtype=float), 0.0, 0.0

        # Rough initial alignment based on centers of mass
        mu_base = pts_base.mean(axis=0)
        mu_moving = pts_moving.mean(axis=0)
        init_trans = np.eye(4, dtype=float)
        init_trans[:3, 3] = mu_base - mu_moving

        # Create Open3D objects
        pcd_base = self._to_o3d(pts_base) 
        pcd_moving = self._to_o3d(pts_moving) 

        # Downsample
        v = self.icp_voxel
        base_down = pcd_base.voxel_down_sample(v) if v > 0 else pcd_base
        moving_down = pcd_moving.voxel_down_sample(v) if v > 0 else pcd_moving

        # Estimate normals
        rad = max(2.5 * v, 0.05)
        base_down.estimate_normals(o3d.geometry.KDTreeSearchParamHybrid(radius=rad, max_nn=30))
        moving_down.estimate_normals(o3d.geometry.KDTreeSearchParamHybrid(radius=rad, max_nn=30))

        # Phase 1: Coarse ICP
        reg_coarse = o3d.pipelines.registration.registration_icp(
            source=moving_down, target=base_down, 
            max_correspondence_distance=self.icp_coarse_corr,
            init=init_trans, 
            estimation_method=o3d.pipelines.registration.TransformationEstimationPointToPoint(),
            criteria=o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=50)
        )

        # Phase 2: Fine ICP
        reg_fine = o3d.pipelines.registration.registration_icp(
            source=moving_down, target=base_down, 
            max_correspondence_distance=self.icp_fine_corr,
            init=reg_coarse.transformation,
            estimation_method=o3d.pipelines.registration.TransformationEstimationPointToPlane(),
            criteria=o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=self.icp_max_iters)
        )

        T = np.asarray(reg_fine.transformation, dtype=float)
        pts_moving_aligned = (pts_moving @ T[:3, :3].T) + T[:3, 3]
        
        return pts_moving_aligned, T, float(reg_fine.fitness), float(reg_fine.inlier_rmse)

    def run_alignment(self, dir_base: str, dir_moving: str, year_base: str, year_moving: str):
        """
        dir_base: The directory containing the reference files (stays fixed).
        dir_moving: The directory containing the files to be moved.
        year_base: String representing the base year (e.g., "2024").
        year_moving: String representing the moving year (e.g., "2023").
        """
        print(f"\n--- Starting Alignment | Moving {year_moving} -> Fixed {year_base} ---")
        
        dir_base = Path(dir_base)
        dir_moving = Path(dir_moving)
        valid_exts = {".laz", ".las"}
        
        files_base = [f for f in dir_base.rglob("*") if f.is_file() and f.suffix.lower() in valid_exts]
        files_moving = [f for f in dir_moving.rglob("*") if f.is_file() and f.suffix.lower() in valid_exts]

        print(f"-> Found {len(files_base)} files in {year_base} (Base).")
        print(f"-> Found {len(files_moving)} files in {year_moving} (Moving).\n")

        if not files_base or not files_moving:
            print("❌ ERROR: Missing point cloud files! Check your paths.")
            return

        # Create dictionary of base files for fast lookup
        dict_base = {f.name: f for f in files_base}
        metrics_list = []

        for f_moving in files_moving:
            name_moving = f_moving.name
            
            # Predict what the equivalent base file should be named
            name_base = name_moving.replace(year_moving, year_base)

            if name_base not in dict_base:
                print(f"[SKIP] No matching {year_base} file found for: {name_moving}")
                continue

            f_base = dict_base[name_base]
            
            # Read laz files
            pts_base, head_base = self._read_laz(f_base)
            pts_moving, head_moving = self._read_laz(f_moving)

            start_time = time.time()

            # Execute ICP (Moving aligns to Base)
            aligned_pts, transform, fitness, rmse = self._icp_align_moving_to_base(
                pts_base=pts_base, pts_moving=pts_moving
            )

            elapsed = time.time() - start_time
            trans_dist = np.linalg.norm(transform[:3, 3])

            # Export aligned moving file using its original header
            out_path = self.out_dir / name_moving
            self._export_laz(aligned_pts, head_moving, out_path)

            metrics_list.append({
                "tree_id": name_moving,
                "base_year": year_base,
                "moving_year": year_moving,
                "fitness": round(fitness, 4),
                "rmse_m": round(rmse, 4),
                "moved_dist_m": round(trans_dist, 3),
                "time_s": round(elapsed, 2)
            })
            print(f" Aligned & Exported: {name_moving} | Pts: {len(aligned_pts)} | RMSE: {rmse:.4f}m")

        if not metrics_list:
            print(f"\n ERROR: Files were found, but no names matched between {year_base} and {year_moving}.")
            return

        # Dynamically name the CSV output
        df = pd.DataFrame(metrics_list)
        csv_name = f"icp_metrics_{year_moving}_aligned_to_{year_base}.csv"
        csv_path = self.out_dir / csv_name
        df.to_csv(csv_path, index=False)
        print(f"\n Finished! Metrics saved to {csv_path}")

if __name__ == "__main__":
    
    # 1. Initialize Aligner with just your output directory
    aligner = TreeAligner(
        out_dir="/Users/loiccv/Documents/UQAM/RawTreesSegmented/comparison_test/2025 aligned - 2026 base",
        icp_voxel=0.05
    )

    # Example 1: Align 2025 to 2024 Base
    # aligner.run_alignment(
    #     dir_base="/Users/loiccv/Documents/UQAM/RawTreesSegmented/2024",
    #     dir_moving="/Users/loiccv/Documents/UQAM/RawTreesSegmented/2025",
    #     year_base="2024",
    #     year_moving="2025"
    # )

    # Example 2: Align 2023 to 2024 Base
    aligner.run_alignment(
        dir_base="/Users/loiccv/Documents/UQAM/RawTreesSegmented/2026",
        dir_moving="/Users/loiccv/Documents/UQAM/RawTreesSegmented/2025",
        year_base="2026",
        year_moving="2025"
    )

    # Example 3: Align 2025 to 2026 Base (Future proofing!)
    # aligner.run_alignment(
    #     dir_base="/Users/loiccv/Documents/UQAM/RawTreesSegmented/2026",
    #     dir_moving="/Users/loiccv/Documents/UQAM/RawTreesSegmented/2025",
    #     year_base="2026",
    #     year_moving="2025"
    # )