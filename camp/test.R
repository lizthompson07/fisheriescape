path = paste(here::here(), "/camp/templates/camp/temp/vars.R", sep = "")
source(path)


data = list(dates = dates, counts = counts)
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

# my_graph = dygraphs::dygraph(my_list, main = "New Haven Temperatures")
my_widget = dygraphs::dyRangeSelector(my_graph, dateWindow = range(data[[1]]))

newpath = paste(here::here(), "/camp/templates/camp/temp/test-graph.html", sep = "")
print(newpath)
htmlwidgets::saveWidget(my_widget, file=newpath )

Sys.chmod(newpath, mode = "0777", use_umask = TRUE)
