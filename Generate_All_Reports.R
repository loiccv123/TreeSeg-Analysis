# Load necessary libraries
library(rmarkdown)
library(knitr)
library(gtools)
Sys.setenv(RSTUDIO_PANDOC = "/usr/local/bin")

############################################################################################
#Variables to change
files_to_remove_manually <- ""
# bloc_numbers <- c(1)
bloc_numbers <- c(1,2,3,4,5,6,7,8,9,10,11,12)
month <- "mai"
year <- 2025
base_dir <- "/Users/loiccv/Documents/UQAM/RStudio_1st_project/Markdown/"
setwd(base_dir) # Set working directory once at the beginning 

prev_year <- year - 1
aligned_dir <- file.path(base_dir, "Alignements", paste0(prev_year, " aligned - ", year, " base"))
has_aligned_dir <- dir.exists(aligned_dir)
############################################################################################

for(bloc_number in bloc_numbers) {
  cat("\n#####################################################\n")
  cat("###   STARTING PROCESSING FOR BLOC", bloc_number, "  ###\n")
  cat("#####################################################\n\n")
  
  # directory <- file.path("/Users/loiccv/Documents/UQAM/RawTreesSegmented",paste0(month,"_",year,"_","segmentation_bloc", bloc_number, "_for_html_report"))
  
  raw_dir <- "/Users/loiccv/Documents/UQAM/RawTreesSegmented"
    
  directory <- file.path(
    raw_dir,
    as.character(year),
    paste0(month, "_", year, "_segmentation_bloc", bloc_number, "_for_html_report")
  )
  
  output_dir <- file.path(base_dir,paste0("tree_reports_",month,"_",year, "_bloc", bloc_number))
  summary_name <- paste0("tree_summary_bloc", bloc_number, ".csv")
  summary_file_path <- file.path(base_dir, summary_name)
  
  tree_files <- list.files(path = directory, pattern = '\\.laz$')
  tree_files <- mixedsort(tree_files)
  
  if (file.exists(summary_file_path)) {
    summary_data <- read.csv(summary_file_path, stringsAsFactors = FALSE)
    if("Tree" %in% names(summary_data)) {
      files_to_remove <- c(paste0(summary_data$Tree, ".laz"), files_to_remove_manually)
      tree_files <- setdiff(tree_files, files_to_remove)
    }
  } 
  
  for(tree_file in tree_files) {
    cat("Processing:", tree_file, "for bloc", bloc_number, "\n")
    Sys.sleep(1) # <— small delay to avoid concurrent Chromote sessions
    
    prev_year_filename  <- sub(as.character(year),
                               as.character(prev_year),
                               tree_file, fixed = TRUE)
    prev_year_full_path <- file.path(aligned_dir, prev_year_filename)
    
    prev_year_param <- if (has_aligned_dir && file.exists(prev_year_full_path)) {
      cat("  ↳ Prev-year file found:", prev_year_filename, "\n")
      prev_year_full_path
    } else {
      if (has_aligned_dir)
        cat("  ↳ Prev-year file NOT found:", prev_year_filename, "— comparison skipped.\n")
      ""
    }
    
    output_name <- paste0("report_", gsub("\\.laz$", "", tree_file), ".html")
    
    # Explicitly call the render function from the rmarkdown package
    rmarkdown::render("tree_analysis_template.Rmd",
                      output_file = output_name,
                      output_dir = output_dir,
                      params = list(tree_file = tree_file, 
                                    dir = directory, 
                                    bloc_nub = bloc_number,
                                    prev_year_file = prev_year_param) 
    )
  }
  out <- file.path(base_dir, paste0("index_bloc", bloc_number, ".html")) 
  rmarkdown::render("create_index.Rmd", output_file = out, params = list(csv_file = summary_name, bloc_nb = bloc_number, month = month, year = year))
  cat("✓ Index page generated for bloc", bloc_number, "\n")
}
cat("\n\n✓✓✓ All specified blocs have been processed successfully! ✓✓✓\n")