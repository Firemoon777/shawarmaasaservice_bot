<template>
  <div class="row">
    <MarketItem v-for="item in this.items" :item="item" v-on:itemSelected="itemSelected"/>
  </div>
  <div class="sticky-bottom w-100 mt-3">
    <button id="close" type="button" class="btn btn-primary w-100" v-if="!error" :disabled="!checkout" data-bs-toggle="modal" data-bs-target="#checkoutModal">К заказу ({{total}} ₽)</button>
    <button type="button" class="btn btn-danger w-100" v-if="error" disabled>{{error}}</button>
  </div>
  <!-- Modal -->
  <div class="modal fade" id="checkoutModal" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
  <div class="modal-dialog modal-dialog-scrollable">
    <div class="modal-content">
      <div class="modal-header">
        <h1 class="modal-title fs-5" id="exampleModalLabel">Подтверждение заказа</h1>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>
      <div class="modal-body">

        <div class="card mb-3 w-100" style="height: 100px;" v-for="data in this.cart">
          <div class="row">
            <div class="col-4">
              <img :src="data.image" style="max-width: 100%; height: 100px; object-fit: cover" class="img-fluid rounded-start" alt="...">
            </div>
            <div class="col-8">
              <div class="card-body">
                <h5 class="card-title">{{data.count}}x {{ data.name }}</h5>
                <p class="card-text" v-if="data.id !== 0">{{data.count}} x {{data.price}} ₽ = {{data.count * data.price}} ₽</p>
                <p class="card-text" v-if="data.id === 0">{{data.price}} ₽</p>
              </div>
            </div>
          </div>
        </div>
        <div class="mb-3">
          <label for="orderComment" class="form-label">Комментарий к заказу</label>
          <input type="text" autocomplete="off" class="form-control" id="orderComment" placeholder="Например: Иорданскую без халопеньо для Ларисы" v-model="comment">
        </div>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-primary w-100" v-on:click="order" :disabled="checkout_loading">Заказать ({{total}} ₽)</button>
      </div>
    </div>
  </div>
</div>
</template>

<script>
import axios from "axios";
import MarketItem from "@/components/MarketItem.vue";

export default {
  name: "MarketView",
  components: {MarketItem},
  props: ["event_id"],
  data() {
    return {
      "items": [],
      "cart": {},
      "checkout": false,
      "comment": "",
      "checkout_loading": false,
      "error": ""
    }
  },
  computed: {
    total: function () {
      let result = 0
      for(let key in this.cart) {
        if(key == 0) {
          result += (this.cart[key].price)
        } else {
          result += (this.cart[key].count * this.cart[key].price)
        }
      }
      return result
    },
    request: function () {
      let result = {};
      for(let key in this.cart) {
        result[key] = this.cart[key].count
      }
      return result
    }
  },
  methods: {
    itemSelected: function(key, value) {
      this.error = ""
      if(value.count > 0) {
        this.cart[key] = value
      } else {
        delete this.cart[key]
      }
      if(0 in this.cart) {
        let prices = [];
        for(let key in this.cart) {
          if(key === 0) continue;
          for(let i = 0; i < this.cart[key].count; i++) prices.push(this.cart[key].price)
        }
        prices.sort((a, b) => (b-a))
        console.log(prices)
        this.cart[0].price = 0
        for(let i = 0; i < this.cart[0].count; i++) {
          if(prices[i] <= 0) {
            this.error = "Купонов больше, чем заказа!"
            return
          }
          this.cart[0].price -= prices[i]
        }
      }
      this.checkout = Object.keys(this.cart).length !== 0
      console.log(this.cart)
    },
    order: function() {
      let self = this
      this.checkout_loading = true

      let data = {
        event_id: this.event_id,
        order: this.request,
        comment: this.comment
      }
      axios.post("/market/order", data).then(function (response) {
        console.log(response.data)
        document.getElementById("close").click()
        self.$router.push({path: "/success", query: {error: response.data.error}})
      }).finally(function () {
        self.checkout_loading = false;
      })
    }
  },
  created() {
    let self = this
    axios.get("/market/" + this.event_id).then(function (response) {
      if(response.data.event === "collecting_orders") {
        self.items = response.data.menu
      } else {
        self.$router.push({path: "/error"})
      }
    })
  }
}
</script>

<style scoped>
.sticky-bottom {
  height: 48px;
}
</style>