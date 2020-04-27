# these should all be bilingual exports

### SMALLER ITEMS
# TODO remake models with fields that make sense
# TODO add additional search features (i.e. for item location)
# TODO add edit button beside quantity
# TODO look into using ajax for popout close and refresh function -- talk to David
# TODO Figure out how to have Forms default fill in the field that is the PK with the pk of the current DetailView
# TODO Add confirmation step for deleting files and add admin classes etc

### LARGER ITEMS
# TODO Add Historical model or some way to track history of inventory of each item (ie. track previous additions, subtractions, inventory control updates) --would need a description field for inveotry control comments (ie. "item missing")
# TODO Add Bulk Lending View to checkout (change to "lent out") status multiple items of various quantities all on one page -- how to sort so you can find all items you want also?
# TODO Bulk Check In View to check back in items -- should be easy enough to sort on a person's name and then bulk check back in items you have out

### SOLVED - I THINK
# TODO Fix quantity calculation error in views.py -- see error message there, need to create case for when no values entered yet -- I think I fixed this!~! WOOO
# TODO get file upload function to work properly -- I think I solved this