library(flowCore)
library(ggcyto)
library(gridExtra)

path <- file.path(
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

anonymize_sample <- function(fpath, white_list = essential_fcs_keywords) {
  temp_fpaths <- unzip(fpath, exdir = "/tmp")
  xml_temp_fpath <- temp_fpaths[grep(".*xml$", temp_fpaths)]
  fcs_temp_fpath <- temp_fpaths[grep(".*fcs$", temp_fpaths)]
  sample <- read.FCS(
    fcs_temp_fpath, dataset = 2
  )
  mat <- exprs(sample)
  params <- parameters(sample)
  anonymous_keywords <- keyword(sample)[white_list]
  anonymous_fcs <- new("flowFrame",
    exprs = mat, description = anonymous_keywords,
    parameters = params
  )
  return_values <- c(anonymous_fcs, xml_temp_fpath)
  return(return_values)
}


#res <- anonymize_sample(path, essential_fcs_keywords)
#spill_str <- '10,FL1,FL2,FL3,FL4,FL5,FL6,FL7,FL8,FL9,FL10,1,0.0090000000000000011,0.0030000000000000005,0,0.002,0,0,0,0,0,0.23,1,0.098,0,0.009,0,0,0,0,0,0.074,0.405,1,0,0.10400000000000002,0,0,0,0,0,0.008,0.07,0.272,1,0.038999999999999993,0.001,0,0,0,0,0.004,0.019,0.099,0.562,1,0.001,0.003,0.012,0,0,0,0,0.003,0.09,0,1,0.047,0.053,0,0,0,0,0.003,0.811,0.008,0.601,1,0.113,0,0,0,0,0.001,0.186,0.088,0.099,0.176,1,0,0,0,0,0,0,0.0060000000000000019,0,0,0,1,0.023,0.078,0.181,0.012,0,0.002,0,0,0,0.141,1'
