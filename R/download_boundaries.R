# Download DHS subnational boundaries for every survey in the study.
# Source: DHS Spatial Data Repository (public, no data request needed),
# accessed through the rdhs package.
#
# Output: data/boundaries/<SurveyId>_<layer>.geojson, plus a summary table
# data/boundaries/boundary_summary.csv showing what each file contains.

suppressPackageStartupMessages({
  library(rdhs)
  library(sf)
})

surveys <- c(
  "KE2014DHS", "KE2022DHS",
  "TZ2015DHS", "TZ2022DHS",
  "UG2016DHS", "UG2024MIS",
  "RW2015DHS", "RW2019DHS"
)

out_dir <- "data/boundaries"
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
summary_rows <- list()

for (s in surveys) {
  message("Downloading ", s)
  res <- tryCatch(
    download_boundaries(surveyId = s, method = "sf",
                        quiet_download = TRUE, server_sleep = 10),
    error = function(e) { message("  failed: ", conditionMessage(e)); NULL }
  )
  if (is.null(res)) next

  for (layer in names(res)) {
    shp <- st_make_valid(res[[layer]])
    path <- file.path(out_dir, paste0(s, "_", layer, ".geojson"))
    st_write(shp, path, delete_dsn = TRUE, quiet = TRUE)
    lvl <- if ("LEVELRNK" %in% names(shp)) paste(unique(shp$LEVELRNK), collapse = ";") else NA
    summary_rows[[length(summary_rows) + 1]] <- data.frame(
      survey = s, layer = layer, n_regions = nrow(shp), level_rank = lvl,
      names = paste(head(shp$REGNAME, 60), collapse = "; ")
    )
    message("  ", layer, ": ", nrow(shp), " regions")
  }
}

summary_df <- do.call(rbind, summary_rows)
write.csv(summary_df, file.path(out_dir, "boundary_summary.csv"), row.names = FALSE)
print(summary_df[, c("survey", "layer", "n_regions", "level_rank")])
