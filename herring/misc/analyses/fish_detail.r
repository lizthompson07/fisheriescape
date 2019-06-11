rm(list = ls())

# Import file from local dir
detail = read.csv("C:\\Users\\fishmand\\Projects\\dm_apps\\herring\\misc\\analyses\\raw_data\\GLF_HERRING_HERRING_DETAIL.txt", header=T)

######################################
# legth frequ distribution ###########
###################################

rm(list = ls())
# Import file from local dir
detail = read.csv("C:\\Users\\fishmand\\Projects\\dm_apps\\herring\\misc\\analyses\\raw_data\\length_freq.csv", header=T)
plot(detail, type = 'h')
abline(v = 19.5, col = 'blue', lty = 2)
abline(v = 37, col = 'blue', lty = 2)

my_tot = sum(detail$SumOfNUMBER_AT_LENGTH)
excluded_vals = sum(detail$SumOfNUMBER_AT_LENGTH[detail$LENGTH<19.5 | detail$LENGTH>37 ])

text(locator(1),paste("n =",round(sum(detail$SumOfNUMBER_AT_LENGTH)/1000000,2), "million" ))

text(locator(1),paste("percent excluded from form =", round(excluded_vals/my_tot,4)*100,"%"))
title("Length Frequency Distribution")



################
# Fish Length  #
################
rm(list=ls())
detail = read.csv("C:\\Users\\fishmand\\Projects\\dm_apps\\herring\\misc\\analyses\\raw_data\\GLF_HERRING_HERRING_DETAIL.txt", header=T)

fish_length = detail$FISH_LENGTH
total_obs = length(fish_length)
fish_length_range = range(fish_length*1.05)

length_mean = mean(fish_length)
length_sd = sd(fish_length)
sd1 = c(length_mean - length_sd, length_mean + length_sd)
sd2 = c(length_mean - 2 * length_sd, length_mean + 2*length_sd)

hist_plot = hist(fish_length)
points(hist_plot$mids, hist_plot$counts, type = 'l', add= T)
#abline(v = length_mean, col='red', lwd=2, lty=2)
abline(v = sd1, col='blue', lwd=2, lty=2)
abline(v = sd2, col='green', lwd=2, lty=2)

x = hist_plot$mids
y= hist_plot$counts

x_sort = sort(fish_length)
thres_lower = x_sort[round(total_obs*.025)]
thres_upper = x_sort[total_obs-(round(total_obs*.025))]

polygon(c( x[x>=thres_upper], thres_upper ),  c(y[x>=thres_upper],0 ), col="red")
polygon(c( x[x<=thres_lower], thres_lower ),  c(y[x<=thres_lower],0 ), col="red")

#how many observations fall outside of sd2?
inprob_obs = length(fish_length[fish_length<sd2[1]])+length(fish_length[fish_length>sd2[2]])
inprob_obs/total_obs



################
# Fish weight  #
################
fish_wt = detail$FISH_WEIGHT[is.na(detail$FISH_WEIGHT)==FALSE & detail$FISH_WEIGHT != 0]
total_obs = length(fish_wt)
total_obs
range(fish_wt)
length(fish_wt[fish_wt==2])

wt_mean = mean(fish_wt)
wt_sd = sd(fish_wt)
sd1 = c(wt_mean - wt_sd, wt_mean + wt_sd)
sd2 = c(wt_mean - 2 * wt_sd, wt_mean + 2*wt_sd)

hist_plot = hist(fish_wt)
plot(hist_plot$mids, hist_plot$counts, type = 'l')
abline(v = wt_mean, col='red', lwd=2, lty=2)
abline(v = sd1, col='blue', lwd=2, lty=2)
abline(v = sd2, col='green', lwd=2, lty=2)

sd2
#how many observations fall outside of sd2?
inprob_obs = length(fish_wt[fish_wt<sd2[1]])+length(fish_wt[fish_wt>sd2[2]])
inprob_obs/total_obs

################
# gonad weight  #
################

gonad_wt = detail$GONAD_WEIGHT[is.na(detail$GONAD_WEIGHT)==FALSE & detail$GONAD_WEIGHT > 0]

total_obs = length(gonad_wt)
total_obs
range(gonad_wt)

gwt_mean = mean(gonad_wt)
gwt_sd = sd(gonad_wt)
sd1 = c(gwt_mean - gwt_sd, gwt_mean + gwt_sd)
sd2 = c(gwt_mean - 2 * gwt_sd, gwt_mean + 2*gwt_sd)

hist_plot = hist(gonad_wt)
plot(hist_plot$mids, hist_plot$counts, type = 'l')
abline(v = gwt_mean, col='red', lwd=2, lty=2)
abline(v = sd1, col='blue', lwd=2, lty=2)
abline(v = sd2, col='green', lwd=2, lty=2)
title("Distribution of gonad weight")
sd2
#how many observations fall outside of sd2?
inprob_obs = length(gonad_wt[gonad_wt<sd2[1]])+length(gonad_wt[gonad_wt>sd2[2]])
inprob_obs/total_obs

legend(locator(1),c("mean","sd x 1","sd x 2"), fill = c('red','blue','green'))

##################################
# length to somatic weight ratio #
##################################

rm(list=ls())
detail = read.csv("C:\\Users\\fishmand\\Projects\\dm_apps\\herring\\misc\\analyses\\raw_data\\GLF_HERRING_HERRING_DETAIL.txt", header=T)

my_df = data.frame(Sample = detail$SAMPLING_INFORMATION_ID, length = detail$FISH_LENGTH, weight = detail$FISH_WEIGHT)
# clean up NAs
cond1 = is.na(my_df[,2])==F & my_df[,2]>0
my_df = my_df[cond1,]
cond2 = is.na(my_df[,3])==F & my_df[,3]>0
my_df = my_df[cond2,]
my_df = my_df[order(my_df[,2]),]

plot(weight~length, data = my_df, xlab = "fish lenth", ylab = "somatic weight", pch='.'  )
title("herring length to weight ratio")

# glm is the better model to use because we can use the Gamma dist to model the residuals... however I cannot seem to find a way to get the prediciton intervals if I use predict.glm
# mod1 = glm(weight~log(length), data = my_df, family = Gamma('log') )

mod1 = lm(log(weight)~log(length), data = my_df)#, family = Gamma('log') )
summary(mod1)

####### MODEL THE PREDICTION INTERVALS
new_data = seq(0, max(my_df$length), by=0.05)

#pred_val = predict(mod1, newdata = data.frame(length = new_data))
pred_val = predict(mod1, newdata = data.frame(length = new_data), interval = 'prediction')

###############
new_df = data.frame(length = new_data, exp(pred_val))
#get prediction
points(new_df$length, new_df$fit, type = 'l', col = 'red')

#get lower formula
mod.lower = lm(log(lwr)~log(length), data = new_df )
summary(mod.lower)
curve(exp(mod.lower$coefficients[1] + log(x)*mod.lower$coefficients[2] ), col = 2, lwd = 2, add = T, lty = 2)

#get upper formula
mod.upper = lm(log(upr)~log(length), data = new_df )
summary(mod.upper)
curve(exp(mod.upper$coefficients[1] + log(x)*mod.upper$coefficients[2] ), col = 2, lwd = 2, add = T, lty = 2)
text(locator(1),"log(weight) ~ log(length)")

#########################################################
# somatic weight to gonad weight ratio + maturity level #
#########################################################

rm(list=ls())
detail = read.csv("C:\\Users\\fishmand\\Projects\\dm_apps\\herring\\misc\\analyses\\raw_data\\gonad_past_5_yr.csv", header=T)

my_df = data.frame( fish_wt = detail$FISH_WEIGHT, gonad_wt = detail$GONAD_WEIGHT, mat_level = detail$MATURITY_CODE)

# histogram of gonad weight
hist(my_df$gonad_wt, xlab = "gonad weight")
hist(my_df$gonad_wt, xlab = "gonad weight", breaks = seq(0,195, 1))
axis


# clean up NAs
cond1 = is.na(my_df[,1])==F & my_df[,1]>0
my_df = my_df[cond1,]
cond2 = is.na(my_df[,2])==F & my_df[,2]>0
my_df = my_df[cond2,]
cond3 = my_df[,3]>0
my_df = my_df[cond3,]
my_df[,3] = as.factor(my_df[,3]) # convert mat code to factor

par(mfrow=c(2,4))
for (i in levels(my_df[,3])) {
  plot(gonad_wt~fish_wt, data = my_df[my_df[,3]==i,], xlim = range(my_df[,1]), ylim = range(my_df[,2]), pch =".")
  title(main=paste("Maturity Level", i))
}



#  MATURITY LEVEL 1
dev.off()
i=1
my_xrange = range(my_df[,1][my_df[,3]==i])
my_yrange = range(my_df[,2][my_df[,3]==i])
plot(gonad_wt~fish_wt, data = my_df[my_df[,3]==i,], xlim = my_xrange, ylim = my_yrange, pch = 19)
title(main=paste("Maturity Level", i,"(past 5 years)"))
text(locator(1),paste("n=",length(my_df[,2][my_df[,3]==i])))
# let's not overcomplicate.... gonad wt should not really be above 1 regardless of body weight
lower.limit = 0
upper.limit = 1


#  MATURITY LEVEL 2
dev.off()
i=2
my_xrange = range(my_df[,1][my_df[,3]==i])
my_yrange = range(my_df[,2][my_df[,3]==i])
plot(gonad_wt~fish_wt, data = my_df[my_df[,3]==i,], xlim = my_xrange, ylim = my_yrange, pch = 19)
title(main=paste("Maturity Level", i,"(past 5 years)"))
text(locator(1),paste("n=",length(my_df[,2][my_df[,3]==i])))

mod1 = lm(log(gonad_wt)~log(fish_wt), data = my_df[my_df[,3]==i,])
summary(mod1)
####### MODEL THE PREDICTION INTERVALS
new_data = seq(0, max(my_df$fish_wt), by=0.05)
pred_val = predict(mod1, newdata = data.frame(fish_wt = new_data), interval = 'prediction')
###############
new_df = data.frame(fish_wt = new_data, exp(pred_val))
#get prediction
points(new_df$fish_wt, new_df$fit, type = 'l', col = 'red')
#get lower formula
mod.lower = lm(log(lwr)~log(fish_wt), data = new_df )
summary(mod.lower)
curve(exp(mod.lower$coefficients[1] + log(x)*mod.lower$coefficients[2] ), col = 2, lwd = 2, add = T, lty = 2)
#get upper formula
mod.upper = lm(log(upr)~log(fish_wt), data = new_df )
summary(mod.upper)
curve(exp(mod.upper$coefficients[1] + log(x)*mod.upper$coefficients[2] ), col = 2, lwd = 2, add = T, lty = 2)
text(locator(1),"log(gonad_wt) ~ log(fish_wt)")

print(paste("exp(",mod.upper$coefficients[1]," + log(fish_wt) * ",mod.upper$coefficients[2],")", sep=""))

lower.limit = 0
upper.limit = exp(-4.13529659279963 + log(fish_wt) * 0.901314871086489)


#  MATURITY LEVEL 3
dev.off()
i=3
my_xrange = range(my_df[,1][my_df[,3]==i])
my_yrange = range(my_df[,2][my_df[,3]==i])
plot(gonad_wt~fish_wt, data = my_df[my_df[,3]==i,], xlim = my_xrange, ylim = my_yrange, pch = 19)
title(main=paste("Maturity Level", i,"(past 5 years)"))
text(locator(1),paste("n=",length(my_df[,2][my_df[,3]==i])))

mod1 = lm(log(gonad_wt)~log(fish_wt), data = my_df[my_df[,3]==i,])
summary(mod1)
####### MODEL THE PREDICTION INTERVALS
new_data = seq(0, max(my_df$fish_wt), by=0.05)
pred_val = predict(mod1, newdata = data.frame(fish_wt = new_data), interval = 'prediction')
###############
new_df = data.frame(fish_wt = new_data, exp(pred_val))
#get prediction
points(new_df$fish_wt, new_df$fit, type = 'l', col = 'red')
#get lower formula
mod.lower = lm(log(lwr)~log(fish_wt), data = new_df )
summary(mod.lower)
curve(exp(mod.lower$coefficients[1] + log(x)*mod.lower$coefficients[2] ), col = 2, lwd = 2, add = T, lty = 2)
#get upper formula
mod.upper = lm(log(upr)~log(fish_wt), data = new_df )
summary(mod.upper)
curve(exp(mod.upper$coefficients[1] + log(x)*mod.upper$coefficients[2] ), col = 2, lwd = 2, add = T, lty = 2)
text(locator(1),"log(gonad_wt) ~ log(fish_wt)")

print(paste("exp(",mod.lower$coefficients[1]," + log(fish_wt) * ",mod.lower$coefficients[2],")", sep=""))
print(paste("exp(",mod.upper$coefficients[1]," + log(fish_wt) * ",mod.upper$coefficients[2],")", sep=""))

lower.limit = exp(-9.73232467962432 + log(fish_wt) * 1.89741087890489)
upper.limit = exp(-7.36823392683834 + log(fish_wt) * 1.89014326451594)

#  MATURITY LEVEL 4
dev.off()
i=4
my_xrange = range(my_df[,1][my_df[,3]==i])
my_yrange = range(my_df[,2][my_df[,3]==i])
plot(gonad_wt~fish_wt, data = my_df[my_df[,3]==i,], xlim = my_xrange, ylim = my_yrange, pch = 19)
title(main=paste("Maturity Level", i,"(past 5 years)"))
text(locator(1),paste("n=",length(my_df[,2][my_df[,3]==i])))

mod1 = lm(log(gonad_wt)~log(fish_wt), data = my_df[my_df[,3]==i,])
summary(mod1)
####### MODEL THE PREDICTION INTERVALS
new_data = seq(0, max(my_df$fish_wt), by=0.05)
pred_val = predict(mod1, newdata = data.frame(fish_wt = new_data), interval = 'prediction')
###############
new_df = data.frame(fish_wt = new_data, exp(pred_val))
#get prediction
points(new_df$fish_wt, new_df$fit, type = 'l', col = 'red')
#get lower formula
mod.lower = lm(log(lwr)~log(fish_wt), data = new_df )
summary(mod.lower)
curve(exp(mod.lower$coefficients[1] + log(x)*mod.lower$coefficients[2] ), col = 2, lwd = 2, add = T, lty = 2)
#get upper formula
mod.upper = lm(log(upr)~log(fish_wt), data = new_df )
summary(mod.upper)
curve(exp(mod.upper$coefficients[1] + log(x)*mod.upper$coefficients[2] ), col = 2, lwd = 2, add = T, lty = 2)
text(locator(1),"log(gonad_wt) ~ log(fish_wt)")

print(paste("exp(",mod.lower$coefficients[1]," + log(fish_wt) * ",mod.lower$coefficients[2],")", sep=""))
print(paste("exp(",mod.upper$coefficients[1]," + log(fish_wt) * ",mod.upper$coefficients[2],")", sep=""))

lower.limit = exp(-3.47650267387848 + log(fish_wt) * 1.032305979081)
upper.limit = exp(-1.26270682092335 + log(fish_wt) * 1.01753432622181)

#  MATURITY LEVEL 5
dev.off()
i=5
my_xrange = range(my_df[,1][my_df[,3]==i])
my_yrange = range(my_df[,2][my_df[,3]==i])
plot(gonad_wt~fish_wt, data = my_df[my_df[,3]==i,], xlim = my_xrange, ylim = my_yrange, pch = 19)
title(main=paste("Maturity Level", i,"(past 5 years)"))
text(locator(1),paste("n=",length(my_df[,2][my_df[,3]==i])))

mod1 = lm(log(gonad_wt)~log(fish_wt), data = my_df[my_df[,3]==i,])
summary(mod1)
####### MODEL THE PREDICTION INTERVALS
new_data = seq(0, max(my_df$fish_wt), by=0.05)
pred_val = predict(mod1, newdata = data.frame(fish_wt = new_data), interval = 'prediction')
###############
new_df = data.frame(fish_wt = new_data, exp(pred_val))
#get prediction
points(new_df$fish_wt, new_df$fit, type = 'l', col = 'red')
#get lower formula
mod.lower = lm(log(lwr)~log(fish_wt), data = new_df )
summary(mod.lower)
curve(exp(mod.lower$coefficients[1] + log(x)*mod.lower$coefficients[2] ), col = 2, lwd = 2, add = T, lty = 2)
#get upper formula
mod.upper = lm(log(upr)~log(fish_wt), data = new_df )
summary(mod.upper)
curve(exp(mod.upper$coefficients[1] + log(x)*mod.upper$coefficients[2] ), col = 2, lwd = 2, add = T, lty = 2)
text(locator(1),"log(gonad_wt) ~ log(fish_wt)")

print(paste("exp(",mod.lower$coefficients[1]," + log(fish_wt) * ",mod.lower$coefficients[2],")", sep=""))
print(paste("exp(",mod.upper$coefficients[1]," + log(fish_wt) * ",mod.upper$coefficients[2],")", sep=""))

lower.limit = exp(-5.20139782140475 + log(fish_wt) * 1.57823918381865)
upper.limit = exp(-4.17515855708087 + log(fish_wt) * 1.56631264086027)


#  MATURITY LEVEL 6
dev.off()
i=6
my_xrange = range(my_df[,1][my_df[,3]==i])
my_yrange = range(my_df[,2][my_df[,3]==i])
plot(gonad_wt~fish_wt, data = my_df[my_df[,3]==i,], xlim = my_xrange, ylim = my_yrange, pch = 19)
title(main=paste("Maturity Level", i,"(past 5 years)"))
text(locator(1),paste("n=",length(my_df[,2][my_df[,3]==i])))

mod1 = lm(log(gonad_wt)~log(fish_wt), data = my_df[my_df[,3]==i,])
summary(mod1)
####### MODEL THE PREDICTION INTERVALS
new_data = seq(0, max(my_df$fish_wt), by=0.05)
pred_val = predict(mod1, newdata = data.frame(fish_wt = new_data), interval = 'prediction')
###############
new_df = data.frame(fish_wt = new_data, exp(pred_val))
#get prediction
points(new_df$fish_wt, new_df$fit, type = 'l', col = 'red')
#get lower formula
mod.lower = lm(log(lwr)~log(fish_wt), data = new_df )
summary(mod.lower)
curve(exp(mod.lower$coefficients[1] + log(x)*mod.lower$coefficients[2] ), col = 2, lwd = 2, add = T, lty = 2)
#get upper formula
mod.upper = lm(log(upr)~log(fish_wt), data = new_df )
summary(mod.upper)
curve(exp(mod.upper$coefficients[1] + log(x)*mod.upper$coefficients[2] ), col = 2, lwd = 2, add = T, lty = 2)
text(locator(1),"log(gonad_wt) ~ log(fish_wt)")

print(paste("exp(",mod.lower$coefficients[1]," + log(fish_wt) * ",mod.lower$coefficients[2],")", sep=""))
print(paste("exp(",mod.upper$coefficients[1]," + log(fish_wt) * ",mod.upper$coefficients[2],")", sep=""))

lower.limit = exp(-4.98077570284809 + log(fish_wt) * 1.53819945023286)
upper.limit = exp(-3.99324471338789 + log(fish_wt) * 1.53661353195509)


#  MATURITY LEVEL 7
dev.off()
i=7
my_xrange = range(my_df[,1][my_df[,3]==i])
my_yrange = range(my_df[,2][my_df[,3]==i])
plot(gonad_wt~fish_wt, data = my_df[my_df[,3]==i,], xlim = my_xrange, ylim = my_yrange, pch = 19)
title(main=paste("Maturity Level", i,"(past 5 years)"))
text(locator(1),paste("n=",length(my_df[,2][my_df[,3]==i])))

mod1 = lm(log(gonad_wt)~log(fish_wt), data = my_df[my_df[,3]==i,])
summary(mod1)
####### MODEL THE PREDICTION INTERVALS
new_data = seq(0, max(my_df$fish_wt), by=0.05)
pred_val = predict(mod1, newdata = data.frame(fish_wt = new_data), interval = 'prediction')
###############
new_df = data.frame(fish_wt = new_data, exp(pred_val))
#get prediction
points(new_df$fish_wt, new_df$fit, type = 'l', col = 'red')
#get lower formula
mod.lower = lm(log(lwr)~log(fish_wt), data = new_df )
summary(mod.lower)
curve(exp(mod.lower$coefficients[1] + log(x)*mod.lower$coefficients[2] ), col = 2, lwd = 2, add = T, lty = 2)
#get upper formula
mod.upper = lm(log(upr)~log(fish_wt), data = new_df )
summary(mod.upper)
curve(exp(mod.upper$coefficients[1] + log(x)*mod.upper$coefficients[2] ), col = 2, lwd = 2, add = T, lty = 2)
text(locator(1),"log(gonad_wt) ~ log(fish_wt)")

print(paste("exp(",mod.lower$coefficients[1]," + log(fish_wt) * ",mod.lower$coefficients[2],")", sep=""))
print(paste("exp(",mod.upper$coefficients[1]," + log(fish_wt) * ",mod.upper$coefficients[2],")", sep=""))

lower.limit = exp(-5.89580204167729 + log(fish_wt) * 1.27478993476955)
upper.limit = exp(-2.94435270310896 + log(fish_wt) * 1.19636077686861)

#  MATURITY LEVEL 8
dev.off()
i=8
my_xrange = range(my_df[,1][my_df[,3]==i])
my_yrange = range(my_df[,2][my_df[,3]==i])
plot(gonad_wt~fish_wt, data = my_df[my_df[,3]==i,], xlim = my_xrange, ylim = my_yrange, pch = 19)
title(main=paste("Maturity Level", i,"(past 5 years)"))
text(locator(1),paste("n=",length(my_df[,2][my_df[,3]==i])))

mod1 = lm(log(gonad_wt)~log(fish_wt), data = my_df[my_df[,3]==i,])
summary(mod1)
####### MODEL THE PREDICTION INTERVALS
new_data = seq(0, max(my_df$fish_wt), by=0.05)
pred_val = predict(mod1, newdata = data.frame(fish_wt = new_data), interval = 'prediction')
###############
new_df = data.frame(fish_wt = new_data, exp(pred_val))
#get prediction
points(new_df$fish_wt, new_df$fit, type = 'l', col = 'red')
#get lower formula
mod.lower = lm(log(lwr)~log(fish_wt), data = new_df )
summary(mod.lower)
curve(exp(mod.lower$coefficients[1] + log(x)*mod.lower$coefficients[2] ), col = 2, lwd = 2, add = T, lty = 2)
#get upper formula
mod.upper = lm(log(upr)~log(fish_wt), data = new_df )
summary(mod.upper)
curve(exp(mod.upper$coefficients[1] + log(x)*mod.upper$coefficients[2] ), col = 2, lwd = 2, add = T, lty = 2)
text(locator(1),"log(gonad_wt) ~ log(fish_wt)")

print(paste("exp(",mod.lower$coefficients[1]," + log(fish_wt) * ",mod.lower$coefficients[2],")", sep=""))
print(paste("exp(",mod.upper$coefficients[1]," + log(fish_wt) * ",mod.upper$coefficients[2],")", sep=""))

lower.limit = exp(-7.18685438956137 + log(fish_wt) * 1.40456267851141)
upper.limit = exp(-5.52714180205898 + log(fish_wt) * 1.39515770753421)





#################
# annulus count to length #
#################

rm(list=ls())
detail = read.csv("C:\\Users\\fishmand\\Projects\\dm_apps\\herring\\misc\\analyses\\raw_data\\gonad_past_5_yr.csv", header=T)
# detail = read.csv("C:\\Users\\fishmand\\Projects\\HERmorrhage\\raw data\\GLF_HERRING_HERRING_DETAIL.txt", header=T)
my_df = data.frame(fish_len = detail$FISH_LENGTH, fish_wt = detail$FISH_WEIGHT, ring_count = detail$NUMBER_OF_ANNULI)

# clean up NAs
cond1 = is.na(my_df[,1])==F & my_df[,1]>0
my_df = my_df[cond1,]
cond2 = is.na(my_df[,2])==F & my_df[,2]>0
my_df = my_df[cond2,]
cond3 = is.na(my_df[,3])==F & my_df[,3]>0
my_df = my_df[cond3,]

# what does the range of number of annuli look like?

#  test 22 range of impossibility
min <= 0
max >= 20

#  test 23 range of improbability

plot(1:12, table(my_df$ring_count), type ='l', lty='dotted')

mean = mean(my_df$ring_count)
sd = sd(my_df$ring_count)
sd1 = c(mean - sd, mean + sd)
sd2 = c(mean - 2 * sd, mean + 2*sd)
# based on sd2
min <= 1
max > 10

# test comparison to fish length

plot(ring_count~fish_len, data = my_df, pch = 19)
title(main=paste("Ring count by fish length", "(past 5 years)"))
text(locator(1),paste("n=",length(my_df$ring_count)))

# mod1 = lm(log(ring_count)~log(fish_len), data = my_df)
mod1 = lm(ring_count~fish_len, data = my_df)
summary(mod1)

####### MODEL THE PREDICTION INTERVALS
new_data = seq(0, max(my_df$fish_len), by=0.05)
pred_val = predict(mod1, newdata = data.frame(fish_len = new_data), interval = 'prediction')
###############
new_df = data.frame(fish_len = new_data, pred_val)
#get prediction
points(new_df$fish_len, new_df$fit, type = 'l', col = 'red')
#get lower formula
mod.lower = lm(lwr~fish_len, data = new_df )
summary(mod.lower)
curve(mod.lower$coefficients[1] + x*mod.lower$coefficients[2] , col = 2, lwd = 2, add = T, lty = 2)
#get upper formula
mod.upper = lm(upr~fish_len, data = new_df )
summary(mod.upper)
curve(mod.upper$coefficients[1] + x*mod.upper$coefficients[2] , col = 2, lwd = 2, add = T, lty = 2)
# text(locator(1),"log(ring_count) ~ log(fish_len)")


print(paste("exp(",mod.lower$coefficients[1]," + log(fish_len) * ",mod.lower$coefficients[2],")", sep=""))
print(paste("exp(",mod.upper$coefficients[1]," + log(fish_len) * ",mod.upper$coefficients[2],")", sep=""))



fish_len=500
lower.limit = round(-14.3554448587879 + (fish_len) * 0.0634008000506408)
upper.limit = round(-10.1477660949041 + (fish_len) * 0.0633784283545123)
print(lower.limit)
print(upper.limit)
