from . import models
import math

range_dict = {
    "fish_length":{
        "possible":{
            "min":1,
            "max":600,
            "comments":"range of historical data based on 344097 observations is  17-480mm",
            },
            "probable":{
                "min":50,
                "max":386,
                "comments":"based on 344097 observations of historical data; [mean +- 2 x SD] = [197.5884, 385.8797]; decision was made in meeting with herring group to allow very small measurements THEREFORE the above comment is moot for the lower bound",
            },
        },
        "fish_weight":{
            "possible":{
                "min":1,
                "max":672,
                "comments":"range of historical data based on 317149 observations is  1 g to  672 g",
            },
            "probable":{
                "min":29,
                "max":412,
                "comments":"based on 317149 observations of historical data; [mean +- 2 x SD] = [ 29.63415, 411.96259]",
            },
        },
        "gonad_weight":{
            "possible":{
                "min":0,
                "max":210,
                "comments":"range of historical data based on 280328 observations is  0.1 g to  204.5 g",
            },
            "probable":{
                "min":0,
                "max":89,
                "comments":"based on 280328 observations of historical data; [mean +- 2 x SD] = [-29.63415, 88.16331]",
            },
        },
        "annulus_count":{
            "possible":{
                "min":0,
                "max":20,
                "comments":"range of historical data based on 280328 observations is  0  to  15",
            },
            "probable":{
                "min":1,
                "max":10,
                "comments":" on 22866 observations of historical data; [mean +- 2 x SD] = [0.9677301 9.1288325]",
            },
        },

    }

def run_global_ratio_test(object_test):
    stop = False
    if object_test.test.id == 204:
        if object_test.fish_detail.fish_weight and object_test.fish_detail.fish_length:
            independent = object_test.fish_detail.fish_length
            dependent = object_test.fish_detail.fish_weight
            min = math.exp(-12.978 + 3.18 * math.log(independent))
            max = math.exp(-12.505 + 3.18 * math.log(independent))
        else:
            stop = True

    elif object_test.test.id == 207:
        if object_test.fish_detail.maturity and object_test.fish_detail.fish_weight and object_test.fish_detail.gonad_weight:
            independent = object_test.fish_detail.fish_weight
            dependent = object_test.fish_detail.gonad_weight
            factor = object_test.fish_detail.maturity.id
            print(factor)
            if factor == 1:
                min = 0
                max = 1
            elif factor == 2:
                min = 0
                max = math.exp(-4.13529659279963 + math.log(independent) * 0.901314871086489)
            elif factor == 3:
                min = math.exp(-9.73232467962432 + math.log(independent) * 1.89741087890489)
                max = math.exp(-7.36823392683834 + math.log(independent) * 1.89014326451594)
            elif factor == 4:
                min = math.exp(-3.47650267387848 + math.log(independent) * 1.032305979081)
                max = math.exp(-1.26270682092335 + math.log(independent) * 1.01753432622181)
            elif factor == 5:
                min = math.exp(-5.20139782140475 + math.log(independent) * 1.57823918381865)
                max = math.exp(-4.17515855708087 + math.log(independent) * 1.56631264086027)
            elif factor == 6:
                min = math.exp(-4.98077570284809 + math.log(independent) * 1.53819945023286)
                max = math.exp(-3.99324471338789 + math.log(independent) * 1.53661353195509)
            elif factor == 7:
                min = math.exp(-5.89580204167729 + math.log(independent) * 1.27478993476955)
                max = math.exp(-2.94435270310896 + math.log(independent) * 1.19636077686861)
            elif factor == 8:
                min = math.exp(-7.18685438956137 + math.log(independent) * 1.40456267851141)
                max = math.exp(-5.52714180205898 + math.log(independent) * 1.39515770753421)
        else:
            stop = True

    elif object_test.test.id == 208:
        independent = object_test.fish_detail.fish_length
        dependent = object_test.fish_detail.fish_weight
        min = round(-14.3554448587879 + (independent) * 6.34008000506408E-02)
        max = round(-10.1477660949041 + (independent) * 6.33784283545123E-02)
    else:
        stop = True

    if not stop:
        print("independent={};dependent={};min={}; max={}".format(independent,dependent,min,max))
        print(dependent)
        if dependent < min or dependent > max:
            object_test.test_passed = False
            object_test.accepted = False
        else:
            object_test.test_passed = True
        object_test.save()


def run_test_202(object, object_type): # All mandatory fields complete
    if object_type == "port_sample":
        # START BY DELETING ALL EXISTING SAMPLETEST FOR GIVEN SAMPLE
        models.SampleTest.objects.filter(sample_id=object.id, test_id=202).delete()

        # CREATE BLANK TESTS IN SAMPLETEST
        test = models.SampleTest.objects.create(sample_id=object.id,test_id=202,test_passed=False)

        if object.sampling_protocol and object.sample_date and object.sampler and object.sampler_ref_number and object.total_fish_preserved and object.total_fish_measured:
            test.test_passed = True
            test.save()

    elif object_type == "lab_sample":
        # START BY DELETING ALL EXISTING SAMPLETEST FOR GIVEN SAMPLE
        models.FishDetailTest.objects.filter(fish_detail_id=object.id, test_id=202).delete()

        # CREATE BLANK TESTS IN SAMPLETEST
        test = models.FishDetailTest.objects.create(fish_detail_id=object.id,test_id=202,field_name='global', test_passed=False)

        if object.fish_length and object.fish_weight and object.sex and object.maturity and object.gonad_weight:
            if object.sample.sampling_protocol.sampling_type == 2: # parasite assessment is only needed for at-sea samples
                if object.parasite:
                    test.test_passed = True
            else:
                test.test_passed = True

            test.save()

def run_test_203(object, object_type): # All data points are within their possible range
    if object_type == "lab_sample":
        # START BY DELETING ALL EXISTING SAMPLETEST FOR GIVEN SAMPLE
        models.FishDetailTest.objects.filter(fish_detail_id=object.id, test_id=203).delete()

        # CREATE BLANK TESTS IN SAMPLETEST
        # and start off optimistic
        test = models.FishDetailTest.objects.create(fish_detail_id=object.id,test_id=203,field_name='global', test_passed=True)

        # grab all test 22s related to sample
        test22s = models.FishDetailTest.objects.filter(fish_detail_id=object.id, test_id=22)
        for t in test22s:
            print(t)
            if not t.test_passed:
                t.test_passed = False
                t.save()
                break

def run_test_204(object, object_type): # fish length to weight
    if object_type == "lab_sample":
        # START BY DELETING ALL EXISTING SAMPLETEST FOR GIVEN SAMPLE
        models.FishDetailTest.objects.filter(fish_detail_id=object.id, test_id=204).delete()

        # CREATE BLANK TESTS IN SAMPLETEST
        test = models.FishDetailTest.objects.create(fish_detail_id=object.id,test_id=204,field_name='global', test_passed=False)
        run_global_ratio_test(test)

def run_test_207(object, object_type): # gonad weight, somatic weight and maturity level
    if object_type == "lab_sample":
        # START BY DELETING ALL EXISTING SAMPLETEST FOR GIVEN SAMPLE
        models.FishDetailTest.objects.filter(fish_detail_id=object.id, test_id=207).delete()

        # CREATE BLANK TESTS IN SAMPLETEST
        test = models.FishDetailTest.objects.create(fish_detail_id=object.id,test_id=207,field_name='global', test_passed=False)
        run_global_ratio_test(test)

def run_test_208(object, object_type): # all improbable observations been accepted
    # ORDER THAT THIS TEST IS RUN IS VERY IMPORTANT: MUST BE AFTER 204 AND 207
    if object_type == "lab_sample":
        # START BY DELETING ALL EXISTING SAMPLETEST FOR GIVEN SAMPLE
        models.FishDetailTest.objects.filter(fish_detail_id=object.id, test_id=208).delete()

        # CREATE BLANK TESTS IN SAMPLETEST
        # and start off optimistic
        test = models.FishDetailTest.objects.create(fish_detail_id=object.id,test_id=208,field_name='global', test_passed=True)

        # grab all test related to fish detail
        fish_detail_tests = models.FishDetailTest.objects.filter(fish_detail_id=object.id)
        for t in fish_detail_tests: # kEEP IN MIND THIS WILL INCLUDE OTOLITH SAMPLE TESTS
            if t.accepted == False:
                test.test_passed = False
                test.save()
                break


def run_test_205(object, object_type): # sum of declared samples = sum from length frq count
    if object_type == "port_sample":
        # START BY DELETING ALL EXISTING SAMPLETEST FOR GIVEN SAMPLE
        models.SampleTest.objects.filter(sample_id=object.id, test_id=205).delete()
        # CREATE BLANK TESTS IN SAMPLETEST
        test = models.SampleTest.objects.create(sample_id=object.id,test_id=205,test_passed=False)

        # get list of counts
        count_list = []
        for obj in object.length_frequency_objects.all():
            count_list.append(obj.count)
        # add the sum as context
        count_sum = sum(count_list)

        if count_sum == object.total_fish_measured:
            test.test_passed = True
            test.save()

def run_test_231(object, object_type): # all lab samples processed
    if object_type == "port_sample":
        # START BY DELETING ALL EXISTING SAMPLETEST FOR GIVEN SAMPLE
        models.SampleTest.objects.filter(sample_id=object.id, test_id=231).delete()
        # CREATE BLANK TESTS IN SAMPLETEST
        test = models.SampleTest.objects.create(sample_id=object.id,test_id=231,test_passed=False)
        # resave each fish detail record to run through fishdetail save method
        for fishy in object.fish_details.all():
            print(fishy)
            fishy.save()
        # resave the sample instance to run thought sample save method
        object.save()
        # now conduct the test
        if object.lab_processing_complete == True:
            test.test_passed = True
            test.save()

def run_test_232(object, object_type): # all lab samples processed
    if object_type == "port_sample":
        # START BY DELETING ALL EXISTING SAMPLETEST FOR GIVEN SAMPLE
        models.SampleTest.objects.filter(sample_id=object.id, test_id=232).delete()
        # CREATE BLANK TESTS IN SAMPLETEST
        test = models.SampleTest.objects.create(sample_id=object.id,test_id=232,test_passed=False)

        # resave each fish detail record to run through fishdetail save method
        for fishy in object.fish_details.all():
            fishy.save()
        # resave the sample instance to run thought sample save method
        object.save()
        # now conduct the test
        if object.otolith_processing_complete == True:
            test_232.test_passed = True
            test_232.save()

def run_data_point_tests(fish_detail, field_name):
    stop = False
    # parse field name
    if field_name == "fish_length":
        field = fish_detail.fish_length
    elif field_name == "fish_weight":
        field = fish_detail.fish_weight
    elif field_name == "gonad_weight":
        field = fish_detail.gonad_weight
    elif field_name == "annulus_count":
        field = fish_detail.gonad_weight
    else:
        print("cannot parse field_name")
        stop = true

    if not stop:
        # delete prior test instances
        models.FishDetailTest.objects.filter(fish_detail_id=fish_detail.id, field_name=field_name).delete()

        # create test instance
        test_21 = models.FishDetailTest.objects.create(fish_detail_id=fish_detail.id,test_id=21,test_passed=False, field_name=field_name)
        test_22 = models.FishDetailTest.objects.create(fish_detail_id=fish_detail.id,test_id=22,test_passed=False, field_name=field_name)
        test_23 = models.FishDetailTest.objects.create(fish_detail_id=fish_detail.id,test_id=23,test_passed=False, field_name=field_name)

        # RUN TESTS
        if not field: # no value present
            pass
        else: # continue testing
            test_21.test_passed = True
            test_21.save()
            if field <= range_dict[field_name]['possible']['min'] or field > range_dict[field_name]['possible']['max']:
                pass
            else:
                test_22.test_passed = True
                test_22.save()
                if field <= range_dict[field_name]['probable']['min'] or field > range_dict[field_name]['probable']['max']:
                    test_23.accepted = 0
                else:
                    test_23.test_passed = True
                test_23.save()
