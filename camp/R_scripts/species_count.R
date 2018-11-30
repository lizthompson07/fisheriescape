# set paths
temp_root = paste(here::here(), "camp","templates","camp","temp", sep="/")
vars_path = paste(temp_root, "vars.R", sep = "/")
html_path = paste(temp_root, "temp_report.html", sep = "/")

# clean up destination
# f <- list.files(temp_root, all.files = TRUE, full.names = TRUE, recursive = TRUE)
# file.remove(f)



# bring in data
source(vars_path)
data = list()
data$years = years
data$counts = counts

format = "numeric"
attrs <- list()
attrs$title <- " "
attrs$xlabel <- "Year"
attrs$ylabel <- "Count in thousands"
attrs$labels <- names(data)
attrs$legend <- "auto"
attrs$retainDateWindow <- FALSE
attrs$axes$x <- list()
attrs$axes$x$pixelsPerLabel <- 60
x <- list()
x$attrs <- attrs
# x$scale <- if (format == "date")
#   periodicity$scale
# else NULL
# x$group <- group
x$annotations <- list()
x$shadings <- list()
x$events <- list()
x$format <- format
# attr(x, "time") <- if (format == "date")
#   time
# else NULL
attr(x, "data") <- data
attr(x, "autoSeries") <- 2
names(data) <- NULL
x$data <- data
my_graph = htmlwidgets::createWidget(name = "dygraphs", x = x, width = NULL,
                                     height = NULL, htmlwidgets::sizingPolicy(browser.padding = 20,
                                                                              browser.fill = FALSE), elementId = NULL)

my_widget = dygraphs::dyRangeSelector(my_graph, dateWindow = range(data[[1]]))
htmlwidgets::saveWidget(my_widget, file=html_path)

Sys.chmod(temp_root, "777", use_umask = TRUE)
f <- list.files(temp_root, all.files = TRUE, full.names = TRUE, recursive = TRUE)
Sys.chmod(f, (file.info(f)$mode | "777"))


