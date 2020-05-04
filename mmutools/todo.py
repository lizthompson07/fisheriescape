# these should all be bilingual exports

### SMALLER ITEMS
# TODO fix Quantity UpdateView to work with popouts in both item_detail and directly
# TODO look into using ajax for popout close and refresh function -- talk to David -- see Travel app (urls, views, jsonresponse)
# TODO Add confirmation step for deleting files
# TODO If Item is marked container=TRUE, then container name is added to list of Locations
# TODO file Model - return 'mmutools/{0}_{1}/{2}'.format(instance.item.item_name, instance.item.size, filename) === when size = N/A it reads the / as separator -- write a test for this

### LARGER ITEMS - PRIORITY
# TODO Testing Units so Dev version can be deployed

### OTHER LARGER ITEMS
# TODO remake models with fields that make sense for lending
# TODO Add Historical model or some way to track history of inventory of each item (ie. track previous additions, subtractions, inventory control updates) --would need a description field for inveotry control comments (ie. "item missing")
# TODO Add Bulk Lending View to checkout (change to "lent out") status multiple items of various quantities all on one page -- how to sort so you can find all items you want also?
# TODO Bulk Check In View to check back in items -- should be easy enough to sort on a person's name and then bulk check back in items you have out


### SOLVED - I THINK
# TODO Fix quantity calculation error in views.py -- see error message there, need to create case for when no values entered yet -- I think I fixed this!~! WOOO
# TODO get file upload function to work properly -- I think I mostly solved this -- UpdateView not getting current "item"
# TODO add additional search features (i.e. for item location, size) --- can you have 2 different search filters on a page? (see itm_list.html page)
# TODO Figure out how to have Forms default fill in the field that is the PK with the pk of the current DetailView --in Views use def get_initial(self):
# TODO add edit button beside quantity