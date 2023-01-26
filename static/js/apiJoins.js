
function join_api_arrays(baseArray, fkArray, baseField, fkField, many=false, newName=false) {
  let objKey = ""
  if (newName) {
    objKey = newName;
  } else {
    objKey = baseField.concat("_obj")
  }

  for (let i = 0; i < baseArray.length; i++ ){
    baseArray[i][objKey] = {}

    if (baseArray[i][baseField]) {
      if (many) {
        baseArray[i][objKey] = fkArray.filter(obj => obj[fkField] === baseArray[i][baseField])

      } else {
        Object.assign(baseArray[i][objKey], fkArray.find(obj => obj[fkField] === baseArray[i][baseField]))
      }
    }
  }
  return baseArray
}
