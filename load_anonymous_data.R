library(flowCore)
library(ggplot2)
library(glue)
library(ggcyto, help, pos = 2, lib.loc = NULL)
library(gridExtra)
library(plot.matrix)

fname <- "mock_output/sub-108731871_specimen-unknown/sub-108731871_specimen-unknown_sample.fcs"
csv_name <- "mock_output/sub-108731871_specimen-unknown/sub-108731871_specimen-unknown_compensation.csv"
x <- read.FCS(
  fname,
  alter.name = TRUE,
  transformation = TRUE
)

manual_compensation <- t(as.matrix(read.csv(
  csv_name,
  header = TRUE,
  row.names = 1
)))
spill_str <- "10,FL1,FL2,FL3,FL4,FL5,FL6,FL7,FL8,FL9,FL10,1,0.0089999999999999976,0.0030000000000000005,0,0,0,0,0,0,0,0.23,1,0.098,0,0.009,0,0,0,0,0,0.074,0.395,1,0,0.004,0,0,0,0,0,0.008,0.07,0.272,1,0.001,0.001,0,0,0,0,0.004,0.019,0.099,0.562,1,0.001,0.003,0.022000000000000002,0,0,0,0,0.003,0.09,0,1,0.047,0.113,0,0,0,0,0,0.77100000000000013,0.008,0.581,1,0.14300000000000002,0,0,0,0,0.001,0.17600000000000002,0.088,0.089,0.176,1,0,0,0,0,0,0,0,0,0,0,1,0.023,0.078,0.181,0.012,0,0.002,0,0,0,0.141,1"

summary(x)
autoplot(x, "FS.A", "SS.A", bins = 200, transorm = FALSE) +
  scale_x_continuous(limits = c(0, 1e7)) +
  theme_minimal()

plot(manual_compensation)
comp <- spillover(x)$'$SPILLOVER'
plot(comp)
fluo_names <- paste(paste("FL", 1:10, sep = ""), "A", sep = ".")
colnames(comp) <- fluo_names
colnames(manual_compensation) <- fluo_names

x_comp <- compensate(x, manual_compensation)

channels_of_interest <- c("FL5.A", "FL4.A")
trans_list <- estimateLogicle(x, channels_of_interest)
comp_trans_list <- estimateLogicle(x_comp, channels_of_interest)
#trans <- logicleTransform(
#  transformationId = "Manual transformation",
#  w = 0, a = 0, t = 1048575, m = 4.5
#)
#trans_list <- transformList(channels_of_interest, trans)

N_BINS <- 200
p1 <- autoplot(
  transform(x, trans_list),
  channels_of_interest[[1]],
  channels_of_interest[[2]],
  bins = N_BINS,
  transorm = FALSE
) +
  ggtitle("Uncompensated") +
  theme(plot.title = element_text(hjust = 0.5))

ggsave(
  "plots/raw.png",
  plot = p1,
  width = 10,
  height = 8,
  units = "cm"
)

p2 <- autoplot(
  transform(x_comp, comp_trans_list),
  channels_of_interest[[1]],
  channels_of_interest[[2]],
  bins = N_BINS,
  transform = FALSE
) +
  ggtitle(glue("Compensated")) +
  theme(plot.title = element_text(hjust = 0.5))

ggsave(
  "plots/compensated.png",
  plot = p2,
  width = 10,
  height = 8,
  units = "cm"
)
