import { useHttp } from "@/composables/useHttp"

export default class RoleApi {
  constructor() {}

  async getRoles() {
    return useHttp("/roles", "GET")
  }

  async getRoleRates() {
    return useHttp("/roles_rate", "GET")
  }

  async editRateRole(data) {
    return useHttp("/roles_rate", "POST", data)
  }

  async getFullRoles() {
    return useHttp("/full_roles", "GET")
  }

  async addRoleToUser(role_id, data) {
    return useHttp(`/user_role/${role_id}`, "POST", data)
  }

  async duplicateRole(data) {
    return useHttp(`/duplicate-role`, "POST", data)
  }

  async createRole(data) {
    return useHttp(`/role`, "POST", data)
  }

  async addPermissionToRole(role_id, data) {
    return useHttp(`/assign_permission_to_role/${role_id}`, "POST", data)
  }

  async getPermissions() {
    return useHttp("/permissions", "GET")
  }

  async removePermissionFromRole(role_id, permissions) {
    return useHttp(
      `/delete_permission_from_role/${role_id}`,
      "DELETE",
      permissions
    )
  }

  async getPermissionsForRole(role_id) {
    return useHttp(`/role_permissions/${role_id}`, "GET")
  }
}
