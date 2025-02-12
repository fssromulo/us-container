import { useHttp, usePublicHttp } from "@/composables/useHttp"

export default class UserApi {
  constructor() {}

  async getUsers(cached = true) {
    if (cached) {
      return useHttp("/users", "GET")
    } else {
      return await useHttp("/users", "GET", null, {
        "Cache-Control": "no-cache"
      })
    }
  }

  async getUserById(id) {
    if (!id) return null
    return useHttp(`/user/${id}`, "GET")
  }
  async getPublicUserById(id, account_id) {
    if (!id) return null
    return usePublicHttp(`/user/${id}/${account_id}`, "GET")
  }
  async switchUser(user_id, target_account) {
    return useHttp(`/user/switch/${user_id}/${target_account}`, "PATCH")
  }

  async sendPasswordResetEmail(id) {
    if (!id) return null
    return useHttp(`/user/password_reset/${id}`, "GET")
  }

  async getUserTeamById(id) {
    return useHttp(`/team/${id}`, "GET")
  }

  async getUserAssistantsById(id) {
    return useHttp(`/assistants/${id}`, "GET")
  }

  async deleteTeamMember(id) {
    return useHttp(`/team_member/${id}`, "DELETE")
  }

  async deleteAssistant(id) {
    return useHttp(`/assistant/${id}`, "DELETE")
  }

  async getTeamMemberById(id) {
    return useHttp(`/team_member/${id}`, "GET")
  }

  async getTeamMemberLeadById(id) {
    return useHttp(`/team_member_lead/${id}`, "GET")
  }

  async getAssistantById(id) {
    return useHttp(`/assistant/${id}`, "GET")
  }

  async updateUser(id, data) {
    return useHttp(`/user/${id}`, "PATCH", data)
  }

  async getRoles() {
    return useHttp(`/get_roles`, "GET")
  }

  async updateUserPreference(id, data) {
    return useHttp(`/user/preference/${id}`, "PATCH", data)
  }

  async createUser(data) {
    return useHttp(`/user`, "POST", data)
  }

  async createTeamMember(data) {
    return useHttp(`/team_member`, "POST", data)
  }

  async createAssistant(data) {
    return useHttp(`/assistant`, "POST", data)
  }
}
