export default class IntervalManager {
  constructor() {}

  runFunctionInInterval(func, onTimeout, intervalTime, timeout, ...params) {
    const intervalId = setInterval(async () => {
      const result = await func()
      if (result != null) {
        clearInterval(intervalId)
      }
    }, intervalTime)

    setTimeout(() => {
      clearInterval(intervalId)
      onTimeout()
    }, timeout)

    return intervalId
  }
}
