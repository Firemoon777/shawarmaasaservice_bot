<template>
  <div class="col-12">
    <div class="spinner-border" role="status" v-if="this.event === null || this.orders === null">
        <span class="sr-only"></span>
      </div>
    <div class="card mt-3" v-if="this.event.state === 1">
      <div class="card-body row">
        <input type="datetime-local" v-model="date_input">
        <button
            type="button"
            class="btn btn-primary mt-2"
            :disabled="!date_input"
            v-on:click="prolong()">
          Обновить время окончания
        </button>
      </div>
    </div>

    <div class="card mt-3" v-if="this.event.state === 2">
      <div class="card-body">
        Доступны:
        <div class="form-check" v-for="item in menu">
          <input class="form-check-input" type="checkbox" value="" :id="'item'+item.id" v-model="item.leftover"
                 :checked="item.leftover !== 0">
          <label class="form-check-label" :for="'item'+item.id">
            {{ item.name }}
          </label>
        </div>
        <input type="datetime-local" v-model="date_input"><br/>
        <button
            type="button"
            class="btn btn-primary"
            :disabled="!date_input"
            v-on:click="reorder()">
          Обновить остатки и запустить перезаказ
        </button>
      </div>
    </div>

    <table class="table mt-3">
      <thead>
        <tr>
          <th scope="col">Имя</th>
          <td>Заказ</td>
          <td>Заказ взят</td>
        </tr>
      </thead>
      <tbody>
        <tr v-for="order in this.orders">
          <th scope="row">
            {{order.name}}
            <a :href="'https://t.me/' + order.username" v-if="order.username" target="_blank">@{{order.username}}</a>
          </th>
          <td>
            <div v-for="entry in order.order">
              <b>{{entry.is_ordered ? '[Заказано]' : ''}}</b> {{entry.count}}x {{entry.name}}
            </div>
          </td>
          <td>
            <input type="checkbox" :checked="order.is_taken" disabled>
          </td>
        </tr>
      </tbody>
    </table>

  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "EventView",
  props: ["id"],
  data() {
    return {
      event: null,
      menu: [],
      orders: null,
      loading: false,
      date_input: null
    }
  },
  computed: {
    reorder_request_data: function () {
      let result = {}
      for (let i in this.menu) {
        result[this.menu[i].id] = !!this.menu[i].leftover
      }
      return result
    }
  },
  methods: {
    prolong() {
      let self = this
      this.loading = true
      let data = {
        time: (new Date(this.date_input)).getTime() / 1000
      }
      axios.post("/event/" + this.id + "/prolong", data).then(function (response) {
        window.location.reload()
      }).finally(function (response) {
        self.loading = false
      })
    },
    reorder: function (m) {
      let self = this
      this.loading = true
      let data = {
        time: (new Date(this.date_input)).getTime() / 1000,
        entries: this.reorder_request_data
      }
      axios.post("/event/" + this.id + "/reorder", data).then(function (response) {
        window.location.reload()
      }).finally(function (response) {
        self.loading = false
      })
    }
  },
  created() {
    let self = this
    axios.get("/event/" + this.id).then(function (response) {
      self.event = response.data
    })
    axios.get("/event/" + this.id + '/menu').then(function (response) {
      self.menu = response.data.menu
      for (let item in self.menu) {
        response.data.menu[item].leftover = !!response.data.menu[item].leftover
      }
    })
    axios.get("/event/" + this.id + '/list').then(function (response) {
      self.orders = response.data.orders
    })
  }
}
</script>

<style scoped>

</style>