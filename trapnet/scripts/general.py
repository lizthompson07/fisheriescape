from .. import models


def clean_up_lamprey():
    s150 = models.Species.objects.get(code=150)  # good one
    s151 = models.Species.objects.get(code=151)  # ammocoete
    s152 = models.Species.objects.get(code=152)  # silver
    life_stage_ammocoete, created = models.LifeStage.objects.get_or_create(name="ammocoete")
    life_stage_silver, created = models.LifeStage.objects.get_or_create(name="silver")

    for specimen in s151.specimens.all():
        specimen.species_id = s150.id
        specimen.life_stage_id = life_stage_ammocoete.id
        specimen.save()

    for specimen in s152.specimens.all():
        specimen.species_id = s150.id
        specimen.life_stage_id = life_stage_silver.id
        specimen.save()

    s151.delete()
    s152.delete()


def find_duplicate_scales():
    # get the unique list of scale ids
    specimens = models.Specimen.objects.filter(scale_id_number__isnull=False)
    scale_ids = set([o.scale_id_number for o in specimens])

    for sid in scale_ids:
        if specimens.filter(scale_id_number=sid).count() > 1:
            print(f"duplicate records found for: {sid}")


def annotate_scales():
    # get the unique list of scale ids
    specimens = models.Specimen.objects.filter(scale_id_number__isnull=False)

    for o in specimens:
        o.scale_id_number += f" {o.sample.season}"
        o.save()

    find_duplicate_scales()


def populate_len():
    fl_specimens = models.Specimen.objects.filter(fork_length__isnull=False, length__isnull=True)
    for o in fl_specimens:
        o.length = o.fork_length
        o.length_type = 1
        o.save()

    tot_specimens = models.Specimen.objects.filter(total_length__isnull=False, length__isnull=True)
    for o in tot_specimens:
        o.length = o.total_length
        o.length_type = 2
        o.save()


def reverse_len():
    len_specimens = models.Specimen.objects.filter(fork_length__isnull=True, total_length__isnull=True, length__isnull=False)
    for o in len_specimens:
        if o.length_type == 1:
            o.fork_length = o.length
        else:
            o.total_length = o.length
        o.save()

    problem_specimens_1 = models.Specimen.objects.filter(fork_length__isnull=False, length__isnull=False, length_type=1)
    for o in problem_specimens_1:
        if o.length != o.fork_length:
            print("bad specimen", o.id)
    problem_specimens_2 = models.Specimen.objects.filter(total_length__isnull=False, length__isnull=False, length_type=2)
    for o in problem_specimens_2:
        if o.length != o.total_length:
            print("bad specimen", o.id)


def populate_adipose_condition():
    print("first part:")
    for o in models.Specimen.objects.filter(origin__code__iexact="ha"):
        o.adipose_condition = 0
        o.save()

    print("second part:")
    for o in models.Specimen.objects.filter(origin__code__iexact="w"):
        o.adipose_condition = 1
        o.save()


def check_for_didymo():
    from trapnet import models
    samples = models.Sample.objects.filter(notes__icontains="didymo")
    for sample in samples:
        remarks = sample.notes.lower()
        if "absent" in remarks:
            sample.didymo = 0
        else:
            sample.didymo = 1
        sample.save()

    samples = models.Sample.objects.filter(sweeps__notes__icontains="didymo").distinct()
    for sample in samples:
        remarks = sample.notes.lower()
        if "absent" in remarks:
            sample.didymo = 0
        else:
            sample.didymo = 1
        sample.save()


def samples_to_sub_types():
    sample_fields = [field.name for field in models.Sample._meta.fields]
    sample_fields.remove("id")

    for s in models.Sample.objects.all():
        s.save()
        if s.sample_type == 1:
            sub = s.rst_sample
        elif s.sample_type == 2:
            sub = s.ef_sample
        else:
            sub = s.trapnet_sample

        sub_fields = [f.name for f in sub._meta.fields]
        sub_fields.remove("id")
        for f in sub_fields:
            if f in sample_fields and getattr(s, f):
                setattr(sub, f, getattr(s, f))

        sub.save()


def more_samples_to_sub_types():
    sample_fields = ["air_temp_arrival"]

    for s in models.Sample.objects.all():
        if s.sample_type == 1:
            sub = s.rst_sample
        elif s.sample_type == 2:
            sub = s.ef_sample
        else:
            sub = s.trapnet_sample

        sub_fields = [f.name for f in sub._meta.fields]
        sub_fields.remove("id")
        for f in sub_fields:
            if f in sample_fields and getattr(s, f):
                print(f"migrating {f} to {sub}")
                setattr(sub, f, getattr(s, f))
        sub.save()


def save_the_salmon():
    from alive_progress import alive_bar
    salmon = models.Specimen.objects.filter(species__tsn=161996, smart_river_age__isnull=True).order_by("-sample__arrival_date")
    with alive_bar(salmon.count(), force_tty=True) as bar:  # declare your expected total
        for s in salmon:
            s.save()
            bar()
