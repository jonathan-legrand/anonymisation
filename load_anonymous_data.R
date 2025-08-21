library(flowCore)
library(ggplot2)
library(glue)
library(ggcyto, help, pos = 2, lib.loc = NULL)
library(gridExtra)
library(plot.matrix)

fname <- "mock_output/sub-266181764_specimen-blood/sub-266181764_specimen-blood_sample.fcs"
csv_name <- "mock_output/sub-266181764_specimen-blood/sub-266181764_specimen-blood_compensation.csv"
x <- read.FCS(
  fname,
  alter.name = TRUE,
  transformation = TRUE
)

manual_compensation <- as.matrix(read.csv(
  csv_name,
  header = TRUE,
  row.names = 1
))

summary(x)
autoplot(x, "FS.A", "SS.A", bins = 200, transorm = FALSE) +
  scale_x_continuous(limits = c(0, 1e7)) +
  theme_minimal()

plot(manual_compensation)
x_comp <- compensate(x, manual_compensation)

channels_of_interest <- c("FL5.A", "FL4.A")
trans_list <- estimateLogicle(x, channels_of_interest)
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
  transform(x_comp, trans_list),
  channels_of_interest[[1]],
  channels_of_interest[[2]],
  bins = N_BINS,
  transform = FALSE
) +
  ggtitle(glue("Compensated, source in {source}")) +
  theme(plot.title = element_text(hjust = 0.5))

ggsave(
  "plots/compensated.png",
  plot = p2,
  width = 10,
  height = 8,
  units = "cm"
)
