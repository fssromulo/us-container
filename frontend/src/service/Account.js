import { useHttp } from "@/composables/useHttp"
import { dfl } from "@/service/DateFormat"

export default class AccountService {
  dtoCms(Cms) {
    return Object.assign({}, Cms, {
      created_at: dfl(Cms.created_at),
      modified_at: dfl(Cms.modified_at)
    })
  }

  constructor() {}
}
