library(flowCore)
library(ggcyto)
library(gridExtra)

essential_fcs_keywords <- scan(
  "metadata_white_list.txt",
  what = "character",
  sep = "\n",
  quote = "\"",
  strip.white = TRUE
)

anonymize_sample <- function(fpath, white_list = essential_fcs_keywords) {
  temp_fpaths <- unzip(fpath, exdir = "/tmp")
  xml_temp_fpath <- temp_fpaths[grep(".*xml$", temp_fpaths)]
  fcs_temp_fpath <- temp_fpaths[grep(".*fcs$", temp_fpaths)]
  sample <- read.FCS(
    fcs_temp_fpath,
    dataset = 2,
    transformation = FALSE,
    truncate_max_range = FALSE
  )
  mat <- exprs(sample)
  params <- parameters(sample)
  kws <- keyword(sample)
  pattern <- paste0("\\Q", white_list, "\\E", collapse = "|")  # quote metachars
  matches <- grep(
    pattern,
    names(kws),
    value = TRUE
  )
  anonymous_keywords <- kws[matches]

  anonymous_fcs <- new("flowFrame",
    exprs = mat, description = anonymous_keywords,
    parameters = params
  )
  return_values <- c(anonymous_fcs, xml_temp_fpath)
  return(return_values)
}