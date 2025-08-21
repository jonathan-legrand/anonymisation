library(flowCore)
library(ggplot2)
library(glue)
library(purrr)
library(ggcyto, help, pos = 2, lib.loc = NULL)
library(gridExtra)
library(plot.matrix)
library(patchwork)

fname <- "mock_output/sub-183205182_specimen-blood/sub-183205182_specimen-blood_sample.fcs"
csv_name <- "mock_output/sub-183205182_specimen-blood/sub-183205182_specimen-blood_compensation.csv"
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

summary(x)
autoplot(x, "FS.A", "SS.A", bins = 200, transorm = FALSE) +
  scale_x_continuous(limits = c(0, 1e7)) +
  theme_minimal()

comp <- spillover(x)$'$SPILLOVER'
fluo_names <- paste(paste("FL", 1:10, sep = ""), "A", sep = ".")
colnames(comp) <- fluo_names
colnames(manual_compensation) <- fluo_names

require(gridExtra)
mat1 <- plot(manual_compensation)
mat2 <- plot(comp)

x_comp_manual <- compensate(x, manual_compensation)
x_comp_original <- compensate(x, comp)

channels_of_interest <- c("FL5.A", "FL4.A")
trans_list <- estimateLogicle(x, channels_of_interest)
#trans <- logicleTransform(
#  transformationId = "Manual transformation",
#  w = 0, a = 0, t = 1048575, m = 4.5
#)
#trans_list <- transformList(channels_of_interest, trans)

N_BINS <- 200
width <- 4
height <- 4
xrange <- c(-2, 4)
yrange <- c(-2, 4)

p1 <- autoplot(
  transform(x, trans_list),
  channels_of_interest[[1]],
  channels_of_interest[[2]],
  bins = N_BINS,
  transorm = FALSE
) +
  ggtitle("Uncompensated") +
  theme(plot.title = element_text(hjust = 0.5)) +
  coord_cartesian(xlim = xrange, ylim = yrange)

ggsave(
  "plots/raw.png",
  plot = p1,
  width = width,
  height = height,
  units = "cm"
)

p2 <- autoplot(
  transform(x_comp_original, trans_list),
  channels_of_interest[[1]],
  channels_of_interest[[2]],
  bins = N_BINS,
  transform = FALSE
) +
  ggtitle(glue("Compensated (Default matrix)")) +
  theme(plot.title = element_text(hjust = 0.5)) +
  coord_cartesian(xlim = xrange, ylim = yrange)

ggsave(
  "plots/compensated.png",
  plot = p2,
  width = width,
  height = height,
  units = "cm"
)

p3 <- autoplot(
  transform(x_comp_manual, trans_list),
  channels_of_interest[[1]],
  channels_of_interest[[2]],
  bins = N_BINS,
  transform = FALSE
) +
  ggtitle(glue("Compensated (XML matrix)")) +
  theme(plot.title = element_text(hjust = 0.5)) +
  coord_cartesian(xlim = xrange, ylim = yrange)

ggsave(
  "plots/compensated_manual.png",
  plot = p2,
  width = width,
  height = height,
  units = "cm"
)

plots <- list(p1, p2, p3)
plots <- map(plots, as.ggplot)
wrap_plots(
  plots,
  ncol = 3,
  heights = c(2, 2, 2)
)
