library(flowCore)
library(ggcyto)
library(gridExtra)

fpath <- file.path(
  "mock_dataset",
  "Lefèvre_Rousseau Léa Moelle bla bla-bla_bla 8903.analysis"
)

essential_fcs_keywords <- scan(
  "metadata_white_list.txt",
  what = "character",
  sep = "\n",
  quote = "\"",
  strip.white = TRUE
)

white_list <- essential_fcs_keywords

#anonymize_sample <- function(fpath, white_list) {
temp_fpaths <- unzip(fpath, exdir = "/tmp")
xml_temp_fpath <- temp_fpaths[grep(".*xml$", temp_fpaths)]
fcs_temp_fpath <- temp_fpaths[grep(".*fcs$", temp_fpaths)]
sample <- read.FCS((fcs_temp_fpath))
mat <- exprs(sample)
params <- parameters(sample)
anonymous_keywords <- description(sample)[essential_fcs_keywords]
anonymous_fcs <- new("flowFrame",
  exprs = mat, description = anonymous_keywords,
  parameters = params
)
