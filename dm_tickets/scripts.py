from .import models


def resave_all_tickets(tickets = models.Ticket.objects.all()):
    for t in tickets:
       t.save()

def resave_all_tickets2(tickets = models.Ticket.objects.all()):

    for t in tickets:
        if t.notes:
            my_ticket = models.Ticket.objects.get(id=t.id)
            my_ticket.notes = my_ticket.notes.replace("**","`")
            my_ticket.save()
