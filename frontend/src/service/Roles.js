import { useUsers } from "../store/modules/users"
import UsersService from "./User"

export default class RolesService {
  constructor() {
    this.userStore = useUsers()
    this.userService = new UsersService()
  }
}
