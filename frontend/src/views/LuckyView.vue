<template>
  <div class="mt-3 mx-auto text-center">
    <p>{{upper_text}}</p>
    <b>{{lower_text}}</b>
  </div>
  <div class="flip-card mt-3 mx-auto">
    <div class="flip-card-inner" :class="this.card_style" v-on:click="flip">
      <div class="card flip-card-front">
        <img src="https://static.wikia.nocookie.net/neonwhite/images/9/9f/Book_of_Life_Soul_Card.png" alt="Avatar" style="width: 100%">
      </div>
      <div class="card flip-card-back" style="height: 100%">
        <img :src="'/api/' + this.item.picture" style="width: 100%" :alt="this.item.name">
        <h3 class="mt-3">{{this.item.name}}</h3>
        <h6 class="mt-3">{{this.item.price}} рублей</h6>
        <div class="h-100"></div>
        <button class="btn btn-light w-75 mx-auto my-3" v-on:click="accept">Принимаю</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "LuckyView",
  data() {
    return {
      clicked: false,
      rotation: 0,
      card_style: {},
      upper_text: "ты просишь",
      lower_text: "ЧУДА",
      item: {},
      lucky_id: null
    }
  },
  props: ["event_id"],
  computed: {
  },
  methods: {
    flip: function () {
      if(this.clicked) return

      this.clicked = true
      let self = this

      self.card_style = {
        shake: true
      }
      self.upper_text = "ты просишь"
      self.lower_text = "ЧУДА"
      axios.post("/lucky/", {event_id: this.event_id}).then(function (response) {
        self.item = response.data.item
        self.lucky_id = response.data.id
      })
      setTimeout(function () {
        self.card_style = {
          shake: false,
          flip: false
        }
        setTimeout(function () {
          self.card_style = {
            shake: false,
            flip: true
          }
          self.upper_text = "прими свой"
          self.lower_text = "ВЫБОР"
        }, 100)
        // self.clicked = false
      }, 3000)
      this.rotation = 180 - this.rotation
    },
    accept: function () {
      let self = this
      axios.post("/lucky/" + this.lucky_id, {event_id: this.event_id, item_id: this.item.id}).then(function (response) {
        self.$router.push({path: "/success"})
      }).catch(function (error) {
        self.$router.push({path: "/error"})
      })
    }
  },
  mounted() {

  }
}
</script>

<style scoped>
.flip-card {
  background-color: transparent;
  width: 300px;
  height: 400px;
  border: 1px solid #f1f1f1;
  perspective: 1000px; /* Remove this if you don't want the 3D effect */
}

/* This container is needed to position the front and back side */
.flip-card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  text-align: center;
  transition: transform 0.8s;
  transform-style: preserve-3d;
}

 /*Do an horizontal flip when you move the mouse over the flip box container*/
.flip-card:hover .flip-card-inner {
  /*transform: rotateX(180deg);*/
}

.shake {
  animation: shake 0.5s;
  animation-iteration-count: infinite;
}

.flip {
  transform: rotateX(180deg);
}

/* Position the front and back side */
.flip-card-front, .flip-card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  -webkit-backface-visibility: hidden; /* Safari */
  backface-visibility: hidden;
}

/* Style the front side (fallback if image is missing) */
.flip-card-front {
  background-color: #bbb;
  color: black;
}

/* Style the back side */
.flip-card-back {
  /*background-color: dodgerblue;*/
  /*color: white;*/
  transform: rotateX(180deg);
}

@keyframes shake {
  0% { transform: translate(1px, 1px) rotate(0deg); }
  10% { transform: translate(-1px, -2px) rotate(-1deg); }
  20% { transform: translate(-3px, 0px) rotate(1deg); }
  30% { transform: translate(3px, 2px) rotate(0deg); }
  40% { transform: translate(1px, -1px) rotate(1deg); }
  50% { transform: translate(-1px, 2px) rotate(-1deg); }
  60% { transform: translate(-3px, 1px) rotate(0deg); }
  70% { transform: translate(3px, 1px) rotate(-1deg); }
  80% { transform: translate(-1px, -1px) rotate(1deg); }
  90% { transform: translate(1px, 2px) rotate(0deg); }
  100% { transform: translate(1px, -2px) rotate(-1deg); }
}
</style>