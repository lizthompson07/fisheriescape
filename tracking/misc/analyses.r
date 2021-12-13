rm(list = ls())
library(tidyverse)

# Import file from local dir
setwd("C:/Users/fishmand/Downloads")

######################################
# cumulative users over time ###########
###################################

rm(list = ls())
data = read.csv("user report_all.csv", header=T)
data$date_joined <- as.Date(data$date_joined, format = "%m/%d/%Y %H:%M")
class(data$date_joined)
head(data$date_joined)

# Import file from local dir

## Cumulative users
plot(data$date_joined, seq(1,length(data$date_joined)) ,type = 'l',xlab = "Date joined", ylab = "Cumulative users")
text(locator(1),paste("Total users =", length(data$cumulative_users)))
title("DM Apps Users Over Time")



par(mfrow=c(1,2))
### Page visits
rm(list = ls())
data = read.csv("page visit summary_all.csv", header=T)
data$date <- as.Date(data$date, format = "%m/%d/%Y")
data$application_name <- factor(data$application_name)
data <- aggregate(sum_of_page_visits~date, data=data, sum)
plot(data$date,data$sum_of_page_visits,type = 'l',xlab = "Date", ylab = "Total page visits")
title("DM Apps Page Visits per Day")
text(locator(1),paste("avg. visits / day =", round(mean(data$sum_of_page_visits))))

### User Counts
rm(list = ls())
data = read.csv("user summary_all.csv", header=T)
data$date <- as.Date(data$date, format = "%m/%d/%Y")
data$application_name <- factor(data$application_name)
data <- aggregate(user_count~date, data=data, sum)
plot(data$date,data$user_count,type = 'l',xlab = "Date", ylab = "Total daily users")
title("DM Apps Users per Day")
text(locator(1),paste("avg. users / day =", round(mean(data$user_count))))



### Top apps by # users
rm(list = ls())
data = read.csv("user summary_all.csv", header=T)
data$date <- as.Date(data$date, format = "%m/%d/%Y")
data$application_name <- factor(data$application_name)
data <- aggregate(user_count~application_name, data=data, sum)
data <- data[rev(order(data$user_count)),][0:10,]
data



### Top apps by # traffic
rm(list = ls())
data = read.csv("page visit summary_all.csv", header=T)
data$date <- as.Date(data$date, format = "%m/%d/%Y")
data$application_name <- factor(data$application_name)
data <- aggregate(sum_of_page_visits~application_name, data=data, mean)
data <- data[rev(order(data$sum_of_page_visits)),][0:10,]
data