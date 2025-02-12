import cloneDeep from "lodash.clonedeep"

const arrayMove = (arr, fromIndex, toIndex) => {
  let newArr = cloneDeep(arr)
  let element = newArr[fromIndex]
  if (element) {
    console.log("element", element)
    newArr.splice(fromIndex, 1)
    newArr.splice(toIndex, 0, element)
    return newArr
  }
}

export default arrayMove
