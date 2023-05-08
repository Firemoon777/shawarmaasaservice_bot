<template>
  <div>
    <div class="mt-3">
      <h1>Ваши заказы</h1>
      <div class="spinner-border" role="status" v-if="this.pending_orders === null">
        <span class="sr-only"></span>
      </div>
      <div class="card mt-3" v-for="order in this.pending_orders">
        <div class="card-header">
          [{{ order.event_date }}] {{ order.chat_name }}
        </div>
        <div class="card-body">
          <div class="card mb-3 w-100" style="height: 100px;" v-for="data in order.data.order">
            <div class="row">
              <div class="col-4">
                <img :src="'/api/' + data.picture" style="max-width: 100%; height: 100px; object-fit: cover"
                     class="img-fluid rounded-start" alt="...">
              </div>
              <div class="col-8">
                <div class="card-body">
                  <h5 class="card-title">{{ data.count }}x {{ data.name }}</h5>
                  <p class="card-text" v-if="data.id !== 0">{{ data.count }} x {{ data.price }} ₽ =
                    {{ data.count * data.price }} ₽</p>
                  <p class="card-text" v-if="data.id === 0">{{ data.price }} ₽</p>
                </div>
              </div>
            </div>
          </div>
          <div class="mt-2" v-if="order.data.comment">
            Комментарий: {{ order.data.comment }}
          </div>
        </div>
      </div>
    </div>
    <div class="mt-3 row" v-if="this.events">
      <h1>События</h1>
      <button type="button" class="btn btn-primary mt-2" v-for="event in this.events"
              v-on:click="this.$router.push({path: '/event/' + event.id})">
        [{{ this.timestamp_to_date(event.order_end_time) }}] {{ event.chat_name }}
      </button>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "RootView",
  data() {
    return {
      pending_orders: null,
      events: null
    }
  },
  methods: {
    timestamp_to_date: function (input) {
      let end_time = new Date(input * 1000)
      console.log(input)
      return end_time.getFullYear() + '-' + (end_time.getMonth() + 1) + '-' + end_time.getDate()
    }
  },
  created() {
    let self = this
    axios.get("/profile/order/pending").then(function (response) {
      self.pending_orders = response.data.orders
    })
    axios.get("/profile/events").then(function (response) {
      self.events = response.data.events
    })
  }
}
</script>

<style scoped>

</style>