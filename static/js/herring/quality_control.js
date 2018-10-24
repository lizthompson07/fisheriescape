function markTestPassed(testId) {
  $("#"+testId).text("passed")
  $("#"+testId).addClass("good")
  $("#"+testId).removeClass("bad")
}

function markTestFailed(testId) {
  $("#"+testId).text("failed")
  $("#"+testId).addClass("bad")
  $("#"+testId).removeClass("good")
}

var rangeObject = {
      "fish_length":{
        "possible":{
            "min":1,
            "max":600,
            "comments":"range of historical data based on 344097 observations is  17-480mm",
            },
            "probable":{
                "min":150,
                "max":386,
                "comments":"based on 344097 observations of historical data; [mean +- 2 x SD] = [197.5884, 385.8797]; decision was made in meeting with herring group to allow very small measurements THEREFORE the above comment is moot for the lower bound. Arbitrariliy selected 150 mm as lower bound"
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

function testPossibleRange(objectType) {
  if (objectType == "lab_sample") {
    // grab all test related to fish detail and see if any failed
    testList = [301,304,307]
    for (var i = 0; i < testList.length; i++) {
      if ($("#id_test_"+testList[i]).text() != "passed") {
        markTestFailed("id_test_203")
        break
      }
      else {
        markTestPassed("id_test_203")
      }
    }
  }
}

function testDataPoints(fieldName) {
  var stop = false
  if (fieldName == "fish_length") {
    test = [300,301,302]
  }
  else if (fieldName == "fish_weight"){
    test = [303,304,305]
  }
  else if (fieldName == "gonad_weight"){
    test = [306,307,308]
  }
  else if (fieldName == "annulus_count"){
    test = [309,310,311]
  }
  else {
    // bad fieldName
    stop = true
  }

  // provided a good fieldName was provided
  if (stop == false) {
    // field is not empty
    if ( $("#id_"+fieldName)[0].value == "") {
      markTestFailed("id_test_"+test[0])
      markTestFailed("id_test_"+test[1])
      markTestFailed("id_test_"+test[2])
    }
    else {
      // test 1 is passed
      markTestPassed("id_test_"+test[0])
      fieldValue = Number($("#id_"+fieldName)[0].value)

      // check possible range
      if (fieldValue < rangeObject[fieldName].possible.min || fieldValue > rangeObject[fieldName].possible.max ) {
        markTestFailed("id_test_"+test[1])
        markTestFailed("id_test_"+test[2])
      }
      else{
        // test 2 passed
        markTestPassed("id_test_"+test[1])

        // check probable range
        if (fieldValue < rangeObject[fieldName].probable.min || fieldValue > rangeObject[fieldName].probable.max ) {
          markTestFailed("id_test_"+test[2])
        }
        else {
          // test 3 passed
          markTestPassed("id_test_"+test[2])
        }
      }
    }
  }
}

function testQCPassed(objectType) {
  // make sure to run this as last test
  if (objectType == "lab_sample") {
    // grab all test related to fish detail and see if any failed
    testList = [202,203,208]
    for (var i = 0; i < testList.length; i++) {
      if ($("#id_test_"+testList[i]).text() != "passed") {
        markTestFailed("id_test_201")
        break
      }
      else {
        markTestPassed("id_test_201")
      }
    }
  }
  else if (objectType == "otolith") {
    // grab all test related to fish detail and see if any failed
    testList = [202,203,208]

    //         # grab all test related to fish detail
    //         fish_detail_global_tests = models.FishDetailTest.objects.filter(fish_detail_id=object.id).filter(Q(test_id=211) | Q(test_id=206) | Q(test_id=210) )
    //
    //         for t in fish_detail_global_tests: # Only looking at the tests of interest
    //             if t.test_passed == False:
    //                 test.test_passed = False
    //                 test.save()
    //                 break


    for (var i = 0; i < testList.length; i++) {
      if ($("#id_test_"+testList[i]).innerHTML != "passed") {
        markTestFailed("id_test_20")
        break
      }
      else {
        markTestPassed("id_test_20")
      }
    }
  }
}

function testMandatoryFields(objectType) {
  if (objectType == "port_sample") {
    for (var i = 0; i < $(".mandatory").length; i++) {
      if ($(".mandatory")[i].innerHTML == "" || $(".mandatory")[i].innerHTML == "None") {
        markTestFailed("id_test_230")
        break
      }
      else {
        markTestPassed("id_test_230")
      }
    }
  }
  else if (objectType == "lab_sample") {
    for (var i = 0; i < $(".mandatory").length; i++) {
      if ($(".mandatory")[i].value == "" || $(".mandatory")[i].value == "None") {

        markTestFailed("id_test_202")
        break
      }
      else {
        markTestPassed("id_test_202")

      }
    }
  }
  else if (objectType == "otolith") {
    // if object.otolith_sampler and object.otolith_season and object.annulus_count:
   //             test.test_passed = True
   //             test.save()
   //
  }
}

function test205(lengthFrequencySum, totalFishMeasured) {
  if (lengthFrequencySum == totalFishMeasured) {
    markTestPassed("id_test_205")

  }
  else {
    markTestFailed("id_test_205")
  }
}

function test231(labProcessingComplete) {
  if (labProcessingComplete) {
    markTestPassed("id_test_231")
  }
  else {
    markTestFailed("id_test_231")
  }

}

function test232(otolithProcessingComplete) {
  if (otolithProcessingComplete) {
    markTestPassed("id_test_232")
  }
  else {
    markTestFailed("id_test_232")
  }
}

function testGlobalRatio(testId) {
  var stop = false
  if (testId == 204) {
    var independentVar = Number($("#id_fish_length")[0].value)
    var dependentVar = Number($("#id_fish_weight")[0].value)
    var independentName = "fish length"
    var dependentName = "fish weight"
    var min = Math.exp(-12.978 + 3.18 * Math.log(independentVar))
    var max = Math.exp(-12.505 + 3.18 * Math.log(independentVar))
    var msgLite = `Improbable measurement for ${independentName} : ${dependentName}`
    var msg = `The ${independentName} : ${dependentName} ratio is outside of the probable range. \n\nFor the given value of ${independentName}, ${dependentName} most commonly ranges between ${parseFloat(Math.round(min * 100) / 100).toFixed(1)} and ${parseFloat(Math.round(max * 100) / 100).toFixed(1)}. \n\nAre you confident in your measurements? \n\nPress [y] for YES or [n] for NO.`
  }
  else if (testId == 204) {
    var independentVar = Number($("#id_fish_length")[0].value)
    var dependentVar = Number($("#id_fish_weight")[0].value)
    var independentName = "fish length"
    var dependentName = "fish weight"
    var min = Math.exp(-12.978 + 3.18 * Math.log(independentVar))
    var max = Math.exp(-12.505 + 3.18 * Math.log(independentVar))
    var msgLite = `Improbable measurement for ${independentName} : ${dependentName}`
    var msg = `The ${independentName} : ${dependentName} ratio is outside of the probable range. \n\nFor the given value of ${independentName}, ${dependentName} most commonly ranges between ${parseFloat(Math.round(min * 100) / 100).toFixed(1)} and ${parseFloat(Math.round(max * 100) / 100).toFixed(1)}. \n\nAre you confident in your measurements? \n\nPress [y] for YES or [n] for NO.`
  }
  else {
    stop = true
  }


  if (stop == false) {
    console.log(`independent=${independentVar};dependent=${dependentVar};min=${min}; max=${max}`);
    if (dependentVar < min || dependentVar > max){
      markTestFailed("id_test_"+testId)
    }
    else {
      markTestPassed("id_test_"+testId)

    }
  }

}


//         if dependent < min or dependent > max:
//             print(123)
//             object_test.test_passed = False
//             if is_accepted == 1:
//                 object_test.accepted = 1
//             # otherwise, not accepted
//             else:
//                 object_test.accepted = 0
//         else:
//             object_test.test_passed = True
//         object_test.save()
//
//     if object_test.accepted is 0:
//         # my_dict[field_name] = {}
//         my_dict["test"] = object_test.test_id
//         my_dict["msg"] = msg
//         my_dict["msg_lite"] = msg_lite
//


// def run_global_ratio_test(object_test, is_accepted):
//     my_dict = {}
//     stop = False
//     if object_test.test.id == 204:
//         if object_test.fish_detail.fish_weight and object_test.fish_detail.fish_length:
//             independent = object_test.fish_detail.fish_length
//             dependent = object_test.fish_detail.fish_weight
//             independent_name = object_test.fish_detail._meta.get_field("fish_length").verbose_name
//             dependent_name = object_test.fish_detail._meta.get_field("fish_weight").verbose_name
//             min = math.exp(-12.978 + 3.18 * math.log(independent))
//             max = math.exp(-12.505 + 3.18 * math.log(independent))
//             msg_lite = "Improbable measurement for {} : {}".format(independent_name,dependent_name)
//             msg = "The {} : {} ratio is outside of the probable range. \\n\\nFor the given value of {}, {} most commonly ranges between {:.2f} and {:.2f}. \\n\\nAre you confident in your measurements? \\n\\nPress [y] for YES or [n] for NO.".format(
//                 independent_name,
//                 dependent_name,
//                 independent_name,
//                 dependent_name,
//                 min,
//                 max,
//             )
//
//         else:
//             stop = True
//
//     elif object_test.test.id == 207:
//         if object_test.fish_detail.maturity and object_test.fish_detail.fish_weight and object_test.fish_detail.gonad_weight != None:
//             independent = object_test.fish_detail.fish_weight
//             dependent = object_test.fish_detail.gonad_weight
//             factor = object_test.fish_detail.maturity.id
//             independent_name = object_test.fish_detail._meta.get_field("fish_weight").verbose_name
//             dependent_name = object_test.fish_detail._meta.get_field("gonad_weight").verbose_name
//             # print(factor)
//             if factor == 1:
//                 min = 0
//                 max = 1
//             elif factor == 2:
//                 min = 0
//                 max = math.exp(-4.13529659279963 + math.log(independent) * 0.901314871086489)
//             elif factor == 3:
//                 min = math.exp(-9.73232467962432 + math.log(independent) * 1.89741087890489)
//                 max = math.exp(-7.36823392683834 + math.log(independent) * 1.89014326451594)
//             elif factor == 4:
//                 min = math.exp(-3.47650267387848 + math.log(independent) * 1.032305979081)
//                 max = math.exp(-1.26270682092335 + math.log(independent) * 1.01753432622181)
//             elif factor == 5:
//                 min = math.exp(-5.20139782140475 + math.log(independent) * 1.57823918381865)
//                 max = math.exp(-4.17515855708087 + math.log(independent) * 1.56631264086027)
//             elif factor == 6:
//                 min = math.exp(-4.98077570284809 + math.log(independent) * 1.53819945023286)
//                 max = math.exp(-3.99324471338789 + math.log(independent) * 1.53661353195509)
//             elif factor == 7:
//                 min = math.exp(-5.89580204167729 + math.log(independent) * 1.27478993476955)
//                 max = math.exp(-2.94435270310896 + math.log(independent) * 1.19636077686861)
//             elif factor == 8:
//                 min = math.exp(-7.18685438956137 + math.log(independent) * 1.40456267851141)
//                 max = math.exp(-5.52714180205898 + math.log(independent) * 1.39515770753421)
//
//             msg_lite = "Improbable measurement for {} : {}".format(independent_name,dependent_name)
//             msg = "The {} : {} ratio is outside of the probable range. \\n\\nFor the given value of {} at maturity level {}, {} most commonly ranges between {:.2f} and {:.2f}. \\n\\nAre you confident in your measurements? \\n\\nPress [y] for YES or [n] for NO.".format(
//                 independent_name,
//                 dependent_name,
//                 independent_name,
//                 factor,
//                 dependent_name,
//                 min,
//                 max,
//             )
//         else:
//             stop = True
//
//     elif object_test.test.id == 209:
//         if object_test.fish_detail.fish_length and object_test.fish_detail.annulus_count:
//             independent = object_test.fish_detail.fish_length
//             dependent = object_test.fish_detail.annulus_count
//             independent_name = object_test.fish_detail._meta.get_field("fish_length").verbose_name
//             dependent_name = object_test.fish_detail._meta.get_field("annulus_count").verbose_name
//             min = (-14.3554448587879 + 6.34008000506408E-02 * independent)
//             max = (-10.1477660949041 + 6.33784283545123E-02 * independent)
//             msg_lite = "Improbable measurement for {} : {}".format(independent_name,dependent_name)
//             msg = "The {} : {} ratio is outside of the probable range. \\n\\nFor the given value of {}, {} most commonly ranges between {:.2f} and {:.2f}. \\n\\nAre you confident in your measurements? \\n\\nPress [y] for YES or [n] for NO.".format(
//                 independent_name,
//                 dependent_name,
//                 independent_name,
//                 dependent_name,
//                 min,
//                 max,
//             )
//
//         else:
//             stop = True
//     else:
//         stop = True
//
//     if not stop:
//         print("independent={};dependent={};min={}; max={}".format(independent,dependent,min,max))
//         if dependent < min or dependent > max:
//             print(123)
//             object_test.test_passed = False
//             if is_accepted == 1:
//                 object_test.accepted = 1
//             # otherwise, not accepted
//             else:
//                 object_test.accepted = 0
//         else:
//             object_test.test_passed = True
//         object_test.save()
//
//     if object_test.accepted is 0:
//         # my_dict[field_name] = {}
//         my_dict["test"] = object_test.test_id
//         my_dict["msg"] = msg
//         my_dict["msg_lite"] = msg_lite
//
//     return my_dict
//
//
//
//

// def run_test_improbable_accepted(object, object_type): # all improbable observations been accepted
//     # ORDER THAT THIS TEST IS RUN IS VERY IMPORTANT: MUST BE AFTER 204 AND 207
//     if object_type == "lab_sample":
//         # START BY DELETING ALL EXISTING SAMPLETEST FOR GIVEN SAMPLE
//         models.FishDetailTest.objects.filter(fish_detail_id=object.id, test_id=208).delete()
//
//         # CREATE BLANK TESTS IN SAMPLETEST
//         # and start off optimistic
//         test = models.FishDetailTest.objects.create(fish_detail_id=object.id,test_id=208,field_name=' global', test_passed=True, scope=1)
//
//         # grab all test related to fish detail
//         fish_detail_tests = models.FishDetailTest.objects.filter(fish_detail_id=object.id)
//         for t in fish_detail_tests: # kEEP IN MIND THIS WILL INCLUDE OTOLITH SAMPLE TESTS
//             if t.accepted == False:
//                 test.test_passed = False
//                 test.save()
//                 break
//
//     elif object_type == "otolith":
//         # START BY DELETING ALL EXISTING SAMPLETEST FOR GIVEN SAMPLE
//         models.FishDetailTest.objects.filter(fish_detail_id=object.id, test_id=211).delete()
//
//         # CREATE BLANK TESTS IN SAMPLETEST
//         # and start off optimistic
//         test = models.FishDetailTest.objects.create(fish_detail_id=object.id,test_id=211,field_name=' global', test_passed=True, scope=2)
//
//         # grab all test related to fish detail
//         fish_detail_tests = models.FishDetailTest.objects.filter(fish_detail_id=object.id)
//         for t in fish_detail_tests: # kEEP IN MIND THIS WILL INCLUDE OTOLITH SAMPLE TESTS
//             if t.accepted == False:
//                 test.test_passed = False
//                 test.save()
//                 break
//
// def run_test_qc_passed(object, object_type): # all quality control tests have been passed
//     # ORDER THAT THIS TEST IS RUN IS VERY IMPORTANT: MUST BE AFTER 202 (mandatory fields), 203 (possible range), 208 (accepted improbable obsverations)
//     if object_type == "lab_sample":
//         # START BY DELETING ALL EXISTING SAMPLETEST FOR GIVEN SAMPLE
//         models.FishDetailTest.objects.filter(fish_detail_id=object.id, test_id=201).delete()
//
//         # CREATE BLANK TESTS IN SAMPLETEST
//         # and start off optimistic
//         test = models.FishDetailTest.objects.create(fish_detail_id=object.id,test_id=201,field_name=' global', test_passed=True, scope=1)
//
//         # grab all test related to fish detail
//         fish_detail_global_tests = models.FishDetailTest.objects.filter(fish_detail_id=object.id).filter(Q(test_id=202) | Q(test_id=203) | Q(test_id=208) )
//
//         for t in fish_detail_global_tests: # Only looking at the tests of interest
//             if t.test_passed == False:
//                 test.test_passed = False
//                 test.save()
//                 break
//
//     elif object_type == "otolith":
//         # START BY DELETING ALL EXISTING SAMPLETEST FOR GIVEN SAMPLE
//         models.FishDetailTest.objects.filter(fish_detail_id=object.id, test_id=200).delete()
//
//         # CREATE BLANK TESTS IN SAMPLETEST
//         # and start off optimistic
//         test = models.FishDetailTest.objects.create(fish_detail_id=object.id,test_id=200,field_name=' global', test_passed=True, scope=2)
//
//         # grab all test related to fish detail
//         fish_detail_global_tests = models.FishDetailTest.objects.filter(fish_detail_id=object.id).filter(Q(test_id=211) | Q(test_id=206) | Q(test_id=210) )
//
//         for t in fish_detail_global_tests: # Only looking at the tests of interest
//             if t.test_passed == False:
//                 test.test_passed = False
//                 test.save()
//                 break
//
//
// def run_data_point_tests(fish_detail, field_name):
//     my_dict = {}
//     stop = False
//     # parse field name
//     if field_name == "fish_length":
//         field = fish_detail.fish_length
//         scope = 1
//     elif field_name == "fish_weight":
//         field = fish_detail.fish_weight
//         scope = 1
//     elif field_name == "gonad_weight":
//         field = fish_detail.gonad_weight
//         scope = 1
//     elif field_name == "annulus_count":
//         field = fish_detail.annulus_count
//         scope = 2
//     else:
//         print("cannot parse field_name")
//         stop = true
//
//     if not stop:
//         # first determine if a test 23 has been accepted
//         try:
//             is_accepted = models.FishDetailTest.objects.filter(fish_detail_id=fish_detail.id, field_name=field_name, test_id=23).first().accepted
//         except Exception as e:
//             print(e)
//             is_accepted = None
//
//         # delete prior test instances
//         models.FishDetailTest.objects.filter(fish_detail_id=fish_detail.id, field_name=field_name).delete()
//
//         # create test instance
//         test_21 = models.FishDetailTest.objects.create(fish_detail_id=fish_detail.id,test_id=21,test_passed=False, field_name=field_name, scope=scope)
//         test_22 = models.FishDetailTest.objects.create(fish_detail_id=fish_detail.id,test_id=22,test_passed=False, field_name=field_name, scope=scope)
//         test_23 = models.FishDetailTest.objects.create(fish_detail_id=fish_detail.id,test_id=23,test_passed=False, field_name=field_name, scope=scope)
//
//         # RUN TESTS
//         if field == None: # no value present; have to use this syntax otherwise a "0" value is excluded
//             pass
//         else: # continue testing
//             test_21.test_passed = True
//             test_21.save()
//             if field < range_dict[field_name]['possible']['min'] or field > range_dict[field_name]['possible']['max']:
//                 pass
//             else:
//                 test_22.test_passed = True
//                 test_22.save()
//                 if field < range_dict[field_name]['probable']['min'] or field > range_dict[field_name]['probable']['max']:
//                     # if the observation was accepted, continue to accept it
//                     if is_accepted == 1:
//                         test_23.accepted = 1
//                     # otherwise, not accepted
//                     else:
//                         test_23.accepted = 0
//
//                 else:
//                     test_23.test_passed = True
//                 test_23.save()
//
//         # if an improbable has not yet been accepted, we have to return a package for the template so that it knows it will have to ask the user to validate observation
//         if test_23.accepted is 0:
//             # my_dict[field_name] = {}
//             my_dict["verbose_name"] = fish_detail._meta.get_field(field_name).verbose_name
//             my_dict["test"] = 23
//             my_dict["msg_lite"] = "Improbable measurement for {}".format(my_dict["verbose_name"])
//             my_dict["msg"] = "{} is outside of the probable range. \\n\\n A value was expected between {} and {}. \\n\\n Are you confident in your measurements? \\n\\n Press [y] for YES or [n] for NO.".format(
//                 my_dict["verbose_name"],
//                 range_dict[field_name]['probable']['min'],
//                 range_dict[field_name]['probable']['max'],
//             )
//         # print(my_dict)
//         return my_dict
