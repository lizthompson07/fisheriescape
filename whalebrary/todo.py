# these should all be bilingual exports

### SMALLER ITEMS
# TODO parent crums logic for ItemTransactionListView -- how
# TODO Parent_crumb logic for TransactionDetailView -- how to get the previous page url if two different urls point to same place?
# TODO see bulk_transaction_list.html -- need another block between table_header and table possibly to cut down repeating? Ask David
# TODO now if there is no location set item_detail view shows an error because of _transaction.html -- fix this (if elseif?)
# TODO personnel_list.html -- colour coding doesn't work for experience level
# TODO redo all views possible with common templates format
# TODO View for items of similar and all sizes (tyvek, gloves, batteries) showing all quantity
# TODO make View for On Order items that you can change status, add location etc all at once for all on order items
# TODO if status=lent out, automatically set Location = lent out
# TODO reports view - if no items in container, don't display table and display message instead (like with _summary pages)

### TICKETED FOR DAVID AND/OR PATRICK
# TODO After editing (commonupdateview) the detail page has a space at the top, but on reload it goes away again -- submit dev ticket
# TODO CommonUpdateView -- gives url error when trying to update -- fixed w redirect -- but how to get success message now?
# TODO DeleteView - shows all related now, but is there a way to get it to prompt and then delete all? Is that from models with cascade? --submit dev ticket

### LARGER ITEMS - PRIORITY
# TODO Testing Units so Dev version can be deployed
# TODO Add lending table to quantity, JS for having lent_to and other fields appear if "lent out" is selected as status
# TODO Lend button beside quantities on item_detail --- form could ask how many, calculate difference etc


### OTHER LARGER ITEMS
# TODO maintenance schedule for certain items (generator, switlik, soundtraps), send email when needed to check?
# TODO If M2M is blank have it show the "---" or None like other fields ((see lib/templatetags/verbose_names, make branch off master to try)
# TODO on _lending.html -- add function to delete a lending (call it 'return') and on return log in eventual historical table with returned date
# TODO Add Bulk Lending View to checkout (change to "lent out") status multiple items of various quantities all on one page -- how to sort so you can find all items you want also?
# TODO Bulk Check In View to check back in items -- should be easy enough to sort on a person's name and then bulk check back in items you have out
# TODO look into using ajax for popout close and refresh function -- talk to David -- see Travel app (urls, views, jsonresponse)


### SOLVED - I THINK
# TODO Fix quantity calculation error in views.py -- see error message there, need to create case for when no values entered yet -- I think I fixed this!~! WOOO
# TODO get file upload function to work properly -- I think I mostly solved this -- UpdateView not getting current "item"
# TODO add additional search features (i.e. for item location, size) --- can you have 2 different search filters on a page? (see itm_list.html page)
# TODO Figure out how to have Forms default fill in the field that is the PK with the pk of the current DetailView --in Views use def get_initial(self):
# TODO add edit button beside quantity
# TODO fix Quantity UpdateView to work with popouts in both item_detail and directly
# TODO file Model - return 'whalebrary/{0}_{1}/{2}'.format(instance.item.item_name, instance.item.size, filename) === when size = N/A it reads the / as separator -- write a test for this
# TODO Be able to click on "Location" in _quantity and take to location_detail page to see address
# TODO Create Location Table (with containers as locations)
# TODO Fix Location view in _quantity.html to go to location_stored detail page != pk
# TODO Add confirmation step for deleting files
# TODO Create and use generic confirm_delete_popout
# TODO Fix all Supplier Views with new M2M model in place -- no longer linked to item --
# TODO why does it add multiple lines in M2M win ListView when multiple things selected -- from views concatenation (remove M2M field)
# TODO Have "Back" button go to previous URL rather than a static page (because you can get there from multiple places now) - <a href="{{ request.META.HTTP_REFERER }}">go back</a>
# TODO When adding a Supplier from item_detail, have it automatically also add it to the item.supplier field
# TODO how to make unique_together = (('item_name', 'size'),) case insensitive? --- see my attempt to save size as lower, but returns error if it's duplicate --made a table for size instead
# TODO remake models with fields that make sense for lending and make items--supplier relation M2M
# TODO make container report - show everything in a container ((see Scifi or iHub  for example))
# TODO on _Supplier.html -- make 'add supplier from existing' view
# TODO Change name of app, can't call us MMU
# TODO how to show what was used -- historical table or other simpler way for now? -- made transaction model
# TODO Add Historical model or some way to track history of inventory of each item (ie. track previous additions, subtractions, inventory control updates) --would need a description field for inveotry control comments (ie. "item missing")
# TODO from location_detail page add link to be able to generate report for that location directly (without having to go to reports) (have to separate for containers and not)
# TODO Ask David if "clear" button can be added to generic_filter
# TODO what if you want to overwrite the name of the 'new' button from generic_filter.html? do you have to copy the whole block?
# TODO "pop" views not working now - looks like integrated into one URL? How to do?

