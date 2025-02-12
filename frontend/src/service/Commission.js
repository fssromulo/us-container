import { useHttp } from "@/composables/useHttp"
import CustomerService from "@/service/Customers"
import formatCurrency from "../utils/formatCurrency"
import { dfl } from "./DateFormat"
import { useUsers } from "../store/modules/users"
import UsersService from "./User"
import UserApi from "@/api/user"
import { DateTime } from "luxon"
import CommissionApi from "@/api/commission"

export default class CommissionService {
  constructor() {
    this.customerService = new CustomerService()
    this.userStore = useUsers()
    this.userService = new UsersService()
    this.userApi = new UserApi()
    this.commissionApi = new CommissionApi()
  }

  getNotClosedCommissionResults = async (
    startDate,
    endDate,
    user_id,
    teamCommission = false
  ) => {
    if (startDate && endDate) {
      startDate = DateTime.fromFormat(startDate, "M/d/yy")
      endDate = DateTime.fromFormat(endDate, "M/d/yy")

      const diff = endDate.diff(startDate, "weeks")
      const start = startDate.toFormat("M/d/yy")
      const end = endDate.toFormat("M/d/yy")

      const url = user_id
        ? `?user_id=${user_id}&start_date=${start}&end_date=${end}&team=${teamCommission}`
        : `?start_date=${start}&end_date=${end}&team=${teamCommission}`
      const { data } = await this.commissionApi.getCommissions(url)
      return data.value
      // }
    }
  }

  updateCommisionPeriodCall = async (
    startDate,
    endDate,
    open,
    teamCommission = false,
    isManagerOnly = true
  ) => {
    if (startDate && endDate) {
      const params = `?start_date=${startDate}&end_date=${endDate}&team=${teamCommission}&open=${open}&is_Manager_Only=${isManagerOnly}`
      const { data } = await this.commissionApi.updateCommissionPeriod(params)
      return data.value
    }
  }

  isUserAssistant = (user_id) => {
    const foundUser = this.userStore.users.find((user) => user.id === user_id)
    return (
      foundUser?.role_id ===
      this.userStore.roles.find(
        (role) => role.name.toLowerCase() === "sales_agent"
      )?.id
    )
  }

  filterOrdersByUser(user, orders) {
    const foundManager = this.userStore.users.find((u) => u.id === user.id)
    let managedUsers =
      foundManager?.manager?.map((m) => {
        return m.assistant
      }) || []

    managedUsers.push(user)
    const filteredOrders = orders.filter((order) => {
      // With how the data is being passed back from the backend, the user will always be the
      // manager, whether they sold it themselves, or if they had an agent under them.
      // so what needs to happen is check if the data contains an assistant object and if it
      // does, then that means this order was sold by an agent and so we need to display that
      // instead
      if (order != null) {
        if (order.assistant_obj == undefined) {
          return managedUsers?.map((u) => u?.id).includes(order.user.id)
        } else {
          return managedUsers
            ?.map((u) => u?.id)
            .includes(order.assistant_obj.id)
        }
      }
    })
    return filteredOrders
  }

  getManagerOrUser(user_id) {
    const currentUser = this.userStore.users.find((u) => u.id === user_id)
    return currentUser?.assistant?.manager
      ? currentUser.assistant.manager
      : currentUser
  }

  getIndividualCommission = async (startDate, endDate, user) => {
    if (startDate && endDate) {
      let closed_orders = await this.commissionApi.getClosedCommissionResults(
        startDate,
        endDate,
        user.id,
        false
      )

      if (closed_orders.data.value.commissions.length > 0) {
        return {
          from_closed: true,
          commissions: closed_orders.data.value.commissions,
          closed_date: closed_orders.data.value.closed_date
        }
      }

      const orders = await this.getNotClosedCommissionResults(
        startDate,
        endDate,
        user.id
      )
      const filteredOrders = this.filterOrdersByUser(user, orders)

      return {
        from_closed: false,
        commissions: filteredOrders
      }
    }
  }

  getTeamCommission = async (startDate, endDate, teamLead) => {
    if (startDate && endDate && teamLead) {
      let closed_orders = await this.commissionApi.getClosedCommissionResults(
        startDate,
        endDate,
        teamLead.id,
        true
      )

      if (closed_orders.data.value.commissions.length > 0) {
        return {
          from_closed: true,
          commissions: closed_orders.data.value.commissions,
          closed_date: closed_orders.data.value.closed_date
        }
      }

      const foundTeamLead = this.userStore.users.find(
        (u) => u.id === teamLead.id
      )
      const userTeam = this.getUserTeam(foundTeamLead)
      if (!userTeam.length) {
        return []
      }

      const orders = await this.getNotClosedCommissionResults(
        startDate,
        endDate,
        null,
        true
      )

      const ordersMappedWithManagers = userTeam
        .map((u) => {
          return this.filterOrdersByUser(u, orders)
          // return orders.filter(o => {
          //   const foundUser = this.userStore.users.find(u => u.id === o.user.id);

          //   return o.user.id === teamLead.id || foundUser?.team_member?.team_lead?.id === teamLead.id
          // })
        })
        .flat(1)

      const deDupedOrders = ordersMappedWithManagers.filter(
        (order, index, self) => {
          return self.findIndex((item) => item.id === order.id) === index
        }
      )

      let finalCommission = deDupedOrders
      return {
        from_closed: false,
        commissions: finalCommission
      }
    }
  }

  getAssistants = (user) => {
    return (
      user?.manager?.map((manager) => {
        return manager.assistant
      }) || []
    )
  }

  getUserTeam = (user) => {
    if (user?.team_lead) {
      return user.team_lead.map((team) => {
        return team.team_member
      })
    }
    return []
  }

  getAllTeamMembers = () => {
    return this.userStore.users.filter((user) => {
      return user.team_member
    })
  }

  mergeLists = (list1, list2) => {
    const list2Dict = {}
    list2.forEach((item) => {
      list2Dict[item.display_order_id] = item
    })

    const mergedList = list1.map((item) => {
      const matchingItem = list2Dict[item.display_order_id]
      if (matchingItem) {
        return {
          ...item,
          ...matchingItem
        }
      }
      return item
    })

    return mergedList
  }

  getRankingsRequest = async (startDate, endDate) => {
    if (startDate && endDate) {
      let deliveredRes, podRes

      if (!this.userStore.isEmulating) {
        deliveredRes = await this.commissionApi.fetchRankings(
          `?start_date=${startDate}&end_date=${endDate}`
        )
      } else {
        deliveredRes = await this.commissionApi.fetchRankings(
          `?emulated_user_id=${this.userStore.currentUser.id}&start_date=${startDate}&end_date=${endDate}`
        )
      }

      let a = deliveredRes.data.value
        .filter((order, index, self) => {
          return self.findIndex((item) => item.id === order.id) === index
        })
        .map((order) => {
          return {
            display_order_id: order.display_order_id,
            agent: order.user.full_name,
            user: order.user,
            units: order.line_item_number_containers,
            sub_total_price: order.calculated_containers_sub_total_price
          }
        })

      return a
    }
  }

  formatRankings = (data) => {
    return data.map((c) => {
      return Object.assign(c, {
        display_sub_total_price: formatCurrency(c.sub_total_price)
      })
    })
  }

  formatIndividualCommission = (data) => {
    return data.map((c) => {
      return Object.assign(c, {
        delivered_at: dfl(c.delivered_at),
        completed_at: dfl(c.completed_at),
        paid_at: dfl(c.paid_at),
        display_sub_total_price: formatCurrency(c.sub_total_price),
        display_profit: formatCurrency(c.calculated_profit, true),
        display_commission_owed: formatCurrency(c.commission_owed),
        display_manager_commission_owed: formatCurrency(
          c.manager_commission_owed
        ),
        display_agent_commission_owed: formatCurrency(
          c.agent_commission_owed,
          true
        )
      })
    })
  }

  formatHighlightCommission = (data) => {
    return data.map((c) => {
      return Object.assign(c, {
        display_sub_total_price: formatCurrency(c.sub_total_price),
        display_commission_owed: formatCurrency(c.commission_owed, true),
        display_manager_commission_owed: formatCurrency(
          c.manager_commission_owed
        ),
        display_agent_commission_owed: formatCurrency(
          c.agent_commission_owed,
          true
        )
      })
    })
  }

  closeCommissions = async (startDate, endDate, isTeam, isManagerOnly) => {
    return await this.updateCommisionPeriodCall(
      startDate,
      endDate,
      false,
      isTeam,
      isManagerOnly
    )
  }

  openCommissionPeriod = async (startDate, endDate, isTeam) => {
    await this.updateCommisionPeriodCall(startDate, endDate, true, isTeam)
  }

  getHighlightCommission = async (
    startDate,
    endDate,
    isTeamCommission,
    isManagerOnly = true
  ) => {
    if (startDate && endDate) {
      let closed_orders = await this.commissionApi.getClosedCommissionResults(
        startDate,
        endDate,
        null,
        isTeamCommission,
        isManagerOnly
      )

      if (closed_orders.data.value.commissions.length > 0) {
        return {
          from_closed: true,
          commissions: closed_orders.data.value.commissions,
          closed_date: closed_orders.data.value.closed_date
        }
      }

      let orders
      if (isTeamCommission) {
        // const teamMembers = this.getAllTeamMembers();

        orders = await this.getNotClosedCommissionResults(
          startDate,
          endDate,
          null,
          true
        )

        orders = orders
          .map((order) => {
            const foundUser = this.userStore.users.find(
              (user) => user.id === order.user.id
            )

            if (!foundUser) {
              return null
            }

            let foundTeamLead
            const managerId = foundUser?.assistant?.manager?.id
            const foundManager = this.userStore.users.find(
              (user) => user.id === managerId
            )
            if (foundManager) {
              foundTeamLead = foundManager?.team_member?.team_lead
            } else {
              foundTeamLead = foundUser?.team_member?.team_lead
            }

            if (!foundTeamLead) {
              return null
            }

            return Object.assign(order, {
              agent: foundTeamLead?.full_name || "",
              user: foundTeamLead
            })
          })
          .filter((order) => order !== null)
      } else {
        orders = await this.getNotClosedCommissionResults(
          startDate,
          endDate,
          null
        )
      }
      let reduced_commision
      if (isManagerOnly) {
        const flats = orders.filter(
          (v, i, a) =>
            a.findIndex((t) => t.display_order_id === v.display_order_id) === i
        )
        reduced_commision = flats.reduce((acc, curr) => {
          const { user, agent, sub_total_price, commission_owed } = curr
          const agentCommission = acc?.find((item) => item.agent === agent)
          if (agentCommission) {
            agentCommission.sub_total_price += sub_total_price
            agentCommission.commission_owed += commission_owed
          } else {
            acc.push({
              user,
              agent,
              sub_total_price,
              commission_owed
            })
          }
          return acc
        }, [])
      } else {
        reduced_commision = orders.reduce((acc, curr) => {
          let {
            user,
            agent,
            assistant,
            manager_commission_owed,
            agent_commission_owed
          } = curr
          const agentCommission = acc?.find((item) => item.agent === agent)
          let assistantCommission = null

          let commission_owed = 0 // this will be the generic commissions var that will be used dynamically by each
          // manager or agent so that we can stay consistent with the way the data is being displayed on the front end

          if (agentCommission) {
            agentCommission.commission_owed += manager_commission_owed
          } else {
            commission_owed = manager_commission_owed
            acc.push({
              user,
              agent,
              commission_owed
            })
          }
          if (assistant != "N/A") {
            // if there is not an assistant on the order, then we will not even look into
            // adding a new item to the array

            // here we have set the agent to the assistant in the case that there was an assistant and
            // so to keep the code consistent, we are searching in the acc array if there is an
            // agent whose name is the assistant and then if there is, we will build upon that array
            assistantCommission = acc?.find((item) => item.agent === assistant)
            if (assistantCommission) {
              assistantCommission.commission_owed += agent_commission_owed
            } else {
              commission_owed = agent_commission_owed
              agent = assistant // this will be so that the assistant is displayed rather than the manager
              acc.push({
                user,
                agent,
                commission_owed
              })
            }
          }
          return acc
        }, [])
      }
      return {
        from_closed: false,
        commissions: reduced_commision
      }
    }
  }

  refreshUsers = async () => {
    if (this.userStore.users.length > 0) return
    const { data } = await this.userApi.getUsers()
    this.userStore.setUsers(data.value.map((u) => this.userService.dtoUser(u)))
  }

  getRankings = async (startDate, endDate, showManagingAgentOnly = false) => {
    if (!startDate || !endDate) return

    let individualRankings = []

    individualRankings = await this.getRankingsRequest(
      startDate.toFormat("M/d/yy"),
      endDate.toFormat("M/d/yy")
    )

    const mappedRankings = individualRankings.map((ranking) => {
      const user = this.userStore.users.find((u) => u.id === ranking.user.id)

      let foundUser
      if (showManagingAgentOnly && user?.assistant?.manager) {
        foundUser = user.assistant.manager
      } else {
        foundUser = user
      }
      if (!foundUser) console.log(ranking)

      return Object.assign(ranking, {
        agent: foundUser?.full_name || "",
        user: foundUser
      })
    })

    return mappedRankings.reduce((acc, curr) => {
      const { agent, units, sub_total_price, user, display_order_id } = curr
      const agentCommission = acc?.find((item) => item.user.id === user?.id)
      if (user)
        if (agentCommission) {
          agentCommission.units += units
          agentCommission.sub_total_price += sub_total_price
        } else {
          acc.push({
            display_order_id,
            agent,
            units,
            sub_total_price,
            user
          })
        }
      else console.log(display_order_id)
      return acc
    }, [])
  }
}
