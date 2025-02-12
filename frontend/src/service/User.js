import { dfl } from "@/service/DateFormat"
import formatPhoneNumber from "../utils/formatPhone"
import { useUsers } from "../store/modules/users"
import { AbilityBuilder } from "@casl/ability"
import { useAuth0 } from "@auth0/auth0-vue"
import { usePublicHttp } from "../composables/useHttp"
import UserApi from "@/api/user"

export default class UsersService {
  constructor() {
    this.userStore = useUsers()
    this.auth0 = useAuth0()
    this.userApi = new UserApi()
  }
  dtoUser(user) {
    const foundRoleName = this.userStore.roles?.find(
      (role) => role.id === user.role_id
    )?.name
    return Object.assign({}, user, {
      created_at: dfl(user.created_at),
      modified_at: dfl(user.modified_at),
      display_is_active: user.is_active ? "Yes" : "No",
      team_lead: user.team_lead?.sort((a, b) =>
        a?.full_name?.localeCompare(b?.full_name)
      ),
      manager: user.manager?.sort((a, b) =>
        a?.full_name?.localeCompare(b?.full_name)
      ),
      phone: formatPhoneNumber(user?.phone) || null,
      sales_link:
        this.userStore.cms?.sales_link_base_url &&
        this.userStore.cms?.sales_link_base_url != ""
          ? `${this.userStore.cms?.sales_link_base_url}${user.id}`
          : "",
      role_name: foundRoleName,
      // assistant_name: user.assistant?.first_name ? `${user.assistant?.first_name} ${user.assistant?.last_name}` : null,
      // team_member_name: user.team_member_name?.first_name ? `${user.team_member?.first_name} ${user.team_member?.last_name}` : null,
      birday: user.birday,
      team_leader_full_name: user.team_leader?.full_name,
      shirt_size: user.shirt_size,
      mailing_address: user.mailing_address
    })
  }

  dtoCommission(user) {
    const mostRecentCommission = user.commission?.sort((a, b) => {
      const dateA = new Date(a.created_at)
      const dateB = new Date(b.created_at)
      return dateB - dateA
    })[0]

    return Object.assign({}, user.commission, {
      flat_commission:
        mostRecentCommission?.flat_commission !== undefined
          ? mostRecentCommission.flat_commission
          : 0,
      commission_percentage:
        mostRecentCommission?.commission_percentage !== undefined
          ? mostRecentCommission.commission_percentage
          : 0,
      commission_effective_date:
        mostRecentCommission?.commission_effective_date !== undefined
          ? dfl(mostRecentCommission.commission_effective_date)
          : null,
      rental_total_flat_commission_rate:
        mostRecentCommission?.rental_total_flat_commission_rate !== undefined
          ? mostRecentCommission.rental_total_flat_commission_rate
          : 0,
      rental_effective_rate:
        mostRecentCommission?.rental_effective_rate !== undefined
          ? mostRecentCommission.rental_effective_rate
          : 0
    })
  }

  updateAbility = ($ability) => {
    console.log("updateAbility")
    const { can, rules } = new AbilityBuilder()

    const mappedCans = this.userStore.currentUser?.permissions.map((p) => {
      const [action, subject] = p.split(":")
      can(action, subject)
    })

    if (mappedCans.length > 0) {
      $ability.update(rules)
    }
  }

  setCurrentUserFromAuthUser = async () => {
    const id = this.auth0.user.value.sub.replace("auth0|", "")
    if (!id) {
      return
    }

    const { data, error } = await this.userApi.getUserById(id)

    if (error.value) {
      await this.auth0.loginWithRedirect()
    }
    const mappedUser = Object.assign({}, data.value, this.auth0.user.value)
    this.userStore.setCurrentUser(this.dtoUser(mappedUser))
  }

  columnOrdering = [
    {
      field: "created_at",
      display: "Created",
      sortable: true,
      style: "max-width: 120px"
    },
    {
      field: "modified_at",
      display: "Modified",
      sortable: true,
      style: "max-width: 120px"
    },
    {
      field: "email",
      display: "Email",
      sortable: true,
      style: "min-width: 300px"
    },
    {
      field: "first_name",
      display: "First Name",
      sortable: true,
      style: "max-width: 200px"
    },
    {
      field: "last_name",
      display: "Last Name",
      sortable: true,
      style: "max-width: 150px"
    },
    {
      field: "phone",
      display: "Phone",
      sortable: true,
      style: "max-width: 200px"
    },
    {
      field: "sales_link",
      display: "Sales Link",
      sortable: true,
      style: "max-width: 300px",
      isButton: true
    },
    {
      field: "send_password_email",
      display: "Send password email",
      sortable: true,
      style: "max-width: 200px",
      isButton: true
    },
    {
      field: "role_name",
      display: "Role",
      sortable: true,
      style: "max-width: 120px"
    },
    {
      field: "display_is_active",
      display: "Active",
      sortable: true,
      style: "max-width: 80px"
    },
    {
      field: "birthday",
      display: "Birthday",
      sortable: true,
      style: "max-width: 80px"
    },
    {
      field: "team_leader_full_name",
      display: "Team Lead",
      sortable: true,
      style: "max-width: 80px"
    },
    {
      field: "shirt_size",
      display: "Shirt Size",
      sortable: true,
      style: "max-width: 80px"
    },
    {
      field: "mailing_address",
      display: "Mailing Address",
      sortable: true,
      style: "max-width: 80px"
    }
  ]
}
