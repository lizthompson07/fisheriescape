from whalesdb.test import WhalesdbFactoryFloor as factory


# this is intended to be used from the `python manage.py shell` to load equipment
# into the sql db just for visual testing of buttons and stuff.
# Use from `python manage.py shell`:
#   from whalesdb.scripts.data_fake import load_fake_equipment
#   load_fake_equipment()
def load_fake_equipment():
    # create a recorder
    eqr = factory.EqrFactory.create()
    # create a hydrophone
    eqh = factory.EqhFactory.create()

    # make them equipment
    eqp_rec = factory.EqpFactory.create(emm=eqr.emm)
    eqp_hyd = factory.EqpFactory.create(emm=eqh.emm)

    # attach the hydrophone to the recorder
    factory.EheFactory.create(rec=eqp_rec, hyd=eqp_hyd)

    # attach the recorder to a deployment
    factory.EdaFactory.create(eqp=eqp_rec)

    # attach to a Calibration Event
    factory.EcaFactory.create(eca_attachment=eqp_rec, eca_hydrophone=eqp_hyd)

    # attach to a technical repair event
    factory.EtrFactory.create(eqp=eqp_rec, hyd=eqp_hyd)


# this is intended to be used from the `python manage.py shell` to load equipment
# into the sql db just for visual testing of buttons and stuff.
# Use from `python manage.py shell`:
#   from whalesdb.scripts.data_fake import load_fake_equipment
#   load_fake_equipment()
def load_fake_station():
    # create a stn
    stn = factory.StnFactory.create()
