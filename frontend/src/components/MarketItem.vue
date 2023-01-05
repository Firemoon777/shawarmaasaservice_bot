<template>
  <div class="col-6 col-sm-4 col-sm-4 col-md-4 col-lg-3 col-xl-3 col-xxl-3 mt-4">
    <div class="card" style="width: 100%">
      <img :src="image_url" class="card-img-top" alt="..." data-bs-toggle="modal" :data-bs-target="'#item-modal-'+item.id" style="max-height: 140px">
      <div class="card-body">
        <h5 class="card-title">{{ item.name }}</h5>

        <div class="row mt-2" v-if="count === 0">
          <button class="btn btn-primary w-100" v-on:click="inc" v-if="count === 0" :disabled="!available">{{ price }}</button>
        </div>
        <div class="row mt-2" v-if="count !== 0">
          <button class="btn btn-primary col-4 counter" v-on:click="dec" >-</button>
          <div class="col-4 counter">{{ count }}</div>
          <button class="btn btn-primary col-4 counter" v-on:click="inc" :disabled="!can_add">+</button>
        </div>
      </div>
    </div>
  </div>
  <!-- Modal -->
  <div class="modal fade" :id="'item-modal-'+item.id" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-scrollable">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5" id="exampleModalLabel">{{ item.name }}</h1>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <img :src="image_url" class="card-img-top" alt="..."/>
          <div class="row"><div class="col-12 mt-3">{{item.description }}</div></div>
          <div class="row">
            <div class="col-12 mt-3">
              <h5>Энергетическая ценность (порция):</h5>
            Жиры: {{ item.fats }}<br>
            Белки: {{ item.proteins }}<br>
            Углеводы: {{ item.carbohydrates }}<br>
            Калории: {{ item.calories }}<br>
            </div>

          </div>
          <div class="row"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "MarketItem",
  props: ["item"],
  emits: ["itemSelected"],
  computed: {
    image_url: function () {
      return '/api/' + this.item.picture
    },
    price: function () {
      if(this.available) {
        return this.item.price + '  ₽'
      }
      return 'Недоступно'
    },
    available: function () {
      return !!this.item.leftover
    },
    can_add: function () {
      return this.count < this.item.leftover
    }
  },
  data() {
    return {
      count: 0
    }
  },
  methods: {
    inc: function() {
      this.count++
      this.notifyParent()
    },
    dec: function() {
      this.count--
      this.notifyParent()
    },
    notifyParent() {
      this.$emit("itemSelected", this.item.id, {
        count: this.count,
        name: this.item.name,
        price: this.item.price,
        image: this.image_url,
        id: this.item.id
      })
    }
  }
}
</script>

<style scoped>
.card-title {
  font-size: 16px;
  height: 38px;
  text-align: center;
}

.counter {
  font-size: 20px;
  text-align: center;
  height: 38px;
}
</style>