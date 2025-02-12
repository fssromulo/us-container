export default class Lock {
  constructor() {
    this.locked = false
    this.queue = []
  }

  async acquire() {
    if (!this.locked) {
      this.locked = true
    } else {
      return new Promise((resolve) => {
        this.queue.push(resolve)
      })
    }
  }

  async release() {
    if (this.queue.length === 0 && this.locked) {
      this.locked = false
      return
    }

    const continuation = this.queue.shift()
    if (typeof continuation === "function") {
      continuation()
    }
  }
}
