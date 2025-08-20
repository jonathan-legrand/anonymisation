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
  alter.name = TRUE
)

spillover(x)
summary(x, digits = digits, maxsum = maxsum)
autoplot(x, "FS.A", "SS.A", bins = 200, transorm = FALSE) +
  scale_x_continuous(limits = c(0, 1e7)) +
  theme_minimal()

comp <- spillover(x)[[1]]
plot(comp)
x_comp <- compensate(x, comp)

channels_of_interest <- c("FL5.A", "FL4.A")
trans_list <- estimateLogicle(x, channels_of_interest)
trans <- logicleTransform(
  transformationId = "Manual transformation",
  w = 0, a = 0, t = 1048575, m = 4.5
)
trans_list <- transformList(channels_of_interest, trans)

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


library(flowCore)
library(ggplot2)

# Convert the flowFrame to a data frame
x_trans <- transform(x_comp, trans_list)
df <- as.data.frame(exprs(x_trans))

# Plot using ggplot
ggplot(df, aes(x = FS.A, y = SS.A)) +
  geom_point(size = 1)
