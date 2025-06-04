library(flowCore)
library(ggplot2)
library(glue)
library(ggcyto, help, pos = 2, lib.loc = NULL)
library(gridExtra)

fname <- "anonymous_fcs/sub-672687964_specimen-marrow/sub-672687964_specimen-marrow_sample.fcs"

x <- read.FCS(fname, alter.name=TRUE)

summary(x, digits = digits, maxsum = maxsum)
autoplot(x, "FS.INT.LIN", "SS.INT.LIN")

comp <- spillover(x)[[1]]
colnames(comp) <- paste(colnames(comp), ".INT.LOG",sep = "")
x_comp <- compensate(x, comp)

channels_of_interest <- c("FL5.INT.LOG","FL4.INT.LOG")
transList <- estimateLogicle(x, channels_of_interest)
p1 <- autoplot(
    transform(x, transList),
    channels_of_interest[[1]], channels_of_interest[[2]]) + ggtitle("Uncompensated")
p2 <- autoplot(
    transform(x_comp, transList),
    channels_of_interest[[1]], channels_of_interest[[2]]) + ggtitle("Compensated")
grid.arrange(as.ggplot(p1), as.ggplot(p2), nrow = 2)#, widths = c(1, 1), heights = c(2, 2))
