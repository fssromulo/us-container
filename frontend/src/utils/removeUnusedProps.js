import isEqual from "lodash.isequal"

const removeUnusedProps = (obj1, obj2) => {
  const changedKeys = Object.keys(obj1).filter(
    (key) => !isEqual(obj1[key], obj2[key])
  )
  let newObj = {}
  changedKeys.forEach((key) => {
    newObj[key] = obj1[key]
  })
  return newObj
}

export default removeUnusedProps
