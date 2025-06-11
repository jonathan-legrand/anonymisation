library(flowCore)
library(ggplot2)
library(glue)
library(ggcyto, help, pos = 2, lib.loc = NULL)
library(gridExtra)
library(plot.matrix)

source <- "line"
fname <- file.path(
  "mock_output",
  "sub-672681965_specimen-marrow",
  "sub-672681965_specimen-marrow_sample.fcs"
)

x <- read.FCS(
  fname,
  alter.name = TRUE,
)

spillover(x)
summary(x, digits = digits, maxsum = maxsum)
autoplot(x, "FS.INT.LIN", "SS.INT.LIN")

comp <- spillover(x)[[1]]
plot(comp)
x_comp <- compensate(x, comp)

channels_of_interest <- c("FL5.INT.LOG", "FL4.INT.LOG")
#trans_list <- estimateLogicle(x, channels_of_interest)
trans <- logicleTransform(
  transformationId = "Manual transformation",
  w = 0, a = 0, t = 1024, m = 4.5
)
trans_list <- transformList(channels_of_interest, trans)
NBINS <- 200
p1 <- autoplot(
  transform(x, trans_list),
  channels_of_interest[[1]],
  channels_of_interest[[2]],
  bins = NBINS
) +
  ggtitle("Uncompensated") +
  theme(plot.title = element_text(hjust = 0.5))

ggsave(
  "plots/plot.png",
  plot = p1,
  width = 10,
  height = 8,
  units = "cm"
)

p2 <- autoplot(
  transform(x_comp, trans_list),
  channels_of_interest[[1]],
  channels_of_interest[[2]],
  bins = NBINS
) +
  ggtitle(glue("Compensated, source in {source}")) +
  theme(plot.title = element_text(hjust = 0.5))

ggsave(
  "plots/plot.png",
  plot = p2,
  width = 10,
  height = 8,
  units = "cm"
)