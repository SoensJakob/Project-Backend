"use strict";
const lanIP = `${window.location.hostname}:5000`;
const IP = `http://${lanIP}`;
const socket = io(IP);

let currentSensorid;
let currentSensornaam;
let currentPeriode = "day"; 
var chart;

//#region ***  DOM references ***
let html_sensors;
let html_date;
let html_menu;
let html_close;
//#endregion

//#region ***  Callback-Visualisation - show___ ***
const showGraph = function (jsonObject) {
  // let timestamps = []
  let waardes = []
  let maximum;
  let periode;
  let SS;
  var date = [];
  let min;
  let max;

  let tijdreeks = jsonObject.device
  for (let t of tijdreeks) {
    let d = new Date(t.timestamp)
    // timestamps.push(d)
    
    waardes.push(t.waarde)
    date.push({x:moment(d),y:t.waarde})
  }
  

  min = date[0].x
  min.set({
    hour: 0,
    minute: 0,
    second: 0
  })
  console.log(min)
  
  if(currentSensorid == 1){
    maximum = 8000
  }
  else if (currentSensorid == 2){
    maximum = 100
  }
  else if (currentSensorid == 3){
    maximum = 100
  }
  else if (currentSensorid == 4){
    maximum = 50
  }

  if (currentPeriode == 'day') {
    periode = 'minute'
    SS = 60
  }
  else{
    periode = 'day'
    SS = 1
  }

  var ctx = document.getElementById('myChart').getContext('2d');
  
  chart = new Chart(ctx, {
    // The type of chart we want to create
    type: 'line',
    // The data for our dataset
    data: {
      datasets: [{
        label: currentSensornaam,
        fill: false,
        borderColor: '#3385FF',
        data: date,
        pointBorderWidth: 0.2,
        pointRadius:2
      }]
    },

    // Configuration options go here
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        xAxes: [{
          bounds: 'ticks',
          source: 'data',
          type: 'time',
          distribution: 'series',
          time: {
            unit: periode,
            round: true,
            stepSize: SS
          },
          maxRotation: 0,
        }],
        yAxes: [{
          ticks: {
            beginAtZero: true,
            max: maximum
          }
        }]
      } 
    }
  });
  
}

const showSensors = function (jsonObject) {
  const sensors = jsonObject.sensors
  // console.log(sensors)
  currentSensorid = sensors[0].device_id
  currentSensornaam = `${sensors[0].naam} (${sensors[0].eenheid})`
  let i = 1;
  
  let htmlstring_sensors = `<h3 class="c-historiek__title">Sensor</h3>
                            <ul class="o-list o-layout">`;
  for (const sensor of jsonObject.sensors) {
    if(i == currentSensorid){
      htmlstring_sensors += `<li tabindex="0"><p class="c-historiek__sensor js-sensor c-historiek__btn c-historiek__btn--active" data-sensor-id="${sensor.device_id}">${sensor.naam} (${sensor.eenheid})</p></li>`;
    }
    else{
      htmlstring_sensors += `<li tabindex="0"><p class="c-historiek__sensor js-sensor c-historiek__btn" data-sensor-id="${sensor.device_id}">${sensor.naam} (${sensor.eenheid})</p></li>`;
    }
    i += 1
  }
  htmlstring_sensors += "</ul>";
  html_sensors.innerHTML = htmlstring_sensors;
  getGraph();
  listenToClickSensors();
}

const showData = function (jsonObject) {
  console.log(jsonObject)

  const data = jsonObject.data

  let dust = data[3].waarde
  let aq = data[2].waarde
  let hum = data[1].waarde
  let temp = data[0].waarde

  
  hum = (hum / 50) * 25
  temp = (temp / 18) * 25
  dust = ((8000 - dust) / 8000) * 25
  aq = ((100 - aq) / 100) * 25

  if (temp > 25){
    let test = temp - 25
    temp = temp - (test * 2)
  }
  if (hum > 25) {
    let test = hum - 25
    hum = hum - (test * 2)
  }
  let algemeneWaarde = Math.round(dust + aq + hum + temp)
  document.querySelector(".js-circle").classList.remove("c-circle__color--g","c-circle__color--lg","c-circle__color--y","c-circle__color--o","c-circle__color--r")
  if (algemeneWaarde > 80) {
    document.querySelector(".js-circle").classList.add("c-circle__color--g")
  }
  else if (60 < algemeneWaarde < 80 ) {
    document.querySelector(".js-circle").classList.add("c-circle__color--lg")
  }
  else if (40 < algemeneWaarde < 60 ) {
    document.querySelector(".js-circle").classList.add("c-circle__color--y")
  }
  else if (20 < algemeneWaarde < 40 ) {
    document.querySelector(".js-circle").classList.add("c-circle__color--o")
  }
  else if (algemeneWaarde < 20 ) {
    document.querySelector(".js-circle").classList.add("c-circle__color--r")
  }


  const waardes = [temp,hum,aq,dust]

  let htmlstring = ""

  for (let i = 0; i < 4; i+=1) {
    htmlstring += `<li class="c-info__item js-info-btn" data-sensor-id=${data[i].device_id} tabindex="0"> `
    if (waardes[i] > 20){
      htmlstring += ` <p class="c-circle c-circle--sm u-color-g u-mt-xl"></p>`
    }
    else if (15 < waardes[i] < 20) {
      
      htmlstring += ` <p class="c-circle c-circle--sm u-color-lg u-mt-lg"></p>
                      <p class="c-circle c-circle--sm u-color-g"></p>`
    }
    else if (10 < waardes[i] < 15) {
      htmlstring += ` <p class="c-circle c-circle--sm u-color-y u-mt-md"></p>
                      <p class="c-circle c-circle--sm u-color-lg"></p>
                      <p class="c-circle c-circle--sm u-color-g"></p>`
    }
    else if (5 < waardes[i] < 25) {
      htmlstring += ` <p class="c-circle c-circle--sm u-color-o u-mt-sm"></p>
                      <p class="c-circle c-circle--sm u-color-y"></p>
                      <p class="c-circle c-circle--sm u-color-lg"></p>
                      <p class="c-circle c-circle--sm u-color-g"></p>`
    }
    else if (waardes[i] < 5) {
      htmlstring += ` <p class="c-circle c-circle--sm u-color-r"></p>
                      <p class="c-circle c-circle--sm u-color-o"></p>
                      <p class="c-circle c-circle--sm u-color-y"></p>
                      <p class="c-circle c-circle--sm u-color-lg"></p>
                      <p class="c-circle c-circle--sm u-color-g"></p>`
    }
      htmlstring += ` <p class="c-info__text">${data[i].afkorting}</p>
                      <p class="c-info__text c-info__text--dark">${data[i].waarde}</p>
                      <p class="c-info__text c-info__text--sm">${data[i].eenheid}</p>
                      </li>`
  }  

  document.querySelector(".js-circle").innerHTML = `${algemeneWaarde}<span class="c-circle--percent">%</span>`
  document.querySelector(".js-info").innerHTML = htmlstring
  listenToClickInfo();
  listenToKeyEventTab();
}

//#endregion

//#region ***  Callback-No Visualisation - callback___  ***

const callbackAutomatic = function(jsonObject) {
  console.log(jsonObject)
}

const callbackError = function(jsonObject) {
  console.log(jsonObject)
}

//#endregion

//#region ***  Data Access - get___ ***
const getGraph = function () {

  let date = html_date.value
  let device_id = currentSensorid
  if (chart) {
    chart.destroy();
  }
  
  if (currentPeriode == "t-month") { 
    handleData(`${IP}/api/v1/${device_id}/3month/${date}`,showGraph);
  }
  else if(currentPeriode == "month") {
    handleData(`${IP}/api/v1/${device_id}/month/${date}`,showGraph);
  }
  else if (currentPeriode == "day") {
    handleData(`${IP}/api/v1/${device_id}/day/${date}`,showGraph);
  }
  
}

const getData = function() {
  handleData(`${IP}/api/v1/data`,showData);
}

const getSensors = function () {
  handleData(`${IP}/api/v1/device/sensors`,showSensors);
}

//#endregion

//#region ***  Event Listeners - listenTo___ ***

const listenToSocket = function () {
  socket.on('connect', function () {
    console.log('verbonden met de socket')
  });

  socket.on('B2F_status_actuators', function (jsonObject) {
    console.log(jsonObject)
    for (const a of jsonObject) {
      const auto = document.querySelector(`.js-auto[data-sensor-id="${a.device_id}"]`)
      const swtch = document.querySelector(`.js-switch[data-sensor-id="${a.device_id}"]`)
      if (a.status == "ON") {
        swtch.checked = true
      }
      else if (a.status == "OFF"){
        swtch.checked = false
      }
      else{ 
        document.querySelector(".c-circle--active").classList.remove("c-circle--active")
        const strength = document.querySelector(`[data-strength ="${a.status}"]`)
        strength.classList.add("c-circle--active")
        swtch.checked = true
      }
      auto.checked = a.automatic
    }
  });
  socket.on('B2F_status_actuator', function(jsonObject){
    console.log(jsonObject)
    const a = jsonObject
    const swtch = document.querySelector(`.js-switch[data-sensor-id="${a.device_id}"]`)
    if (a.status == "ON") {
      swtch.checked = true
    }
    else if (a.status == "OFF"){
      swtch.checked = false
    }
    else{ 
      document.querySelector(".c-circle--active").classList.remove("c-circle--active")
      const strength = document.querySelector(`[data-strength ="${a.status}"]`)
      strength.classList.add("c-circle--active")
      swtch.checked = true
    }
  });

};

const listenToAutomatic = function() {
  const buttons = document.querySelectorAll('.js-auto')
  for (const btn of buttons) {
    btn.addEventListener("click", function(){
      const id = btn.getAttribute("data-sensor-id")
      socket.emit("F2B_switch_automatic", { sensor_id: id, status: btn.checked })
    })
    
  }
}

const listenToManual = function() {
  const buttons = document.querySelectorAll(".js-switch")
  for (const btn of buttons) {
    btn.addEventListener("click", function() {
      const id = btn.getAttribute("data-sensor-id")
      let status = btn.checked
      if (btn.hasAttribute("data-strength")) {
        let test = document.querySelector(".c-circle--active")
        test.classList.remove("c-circle--active")
        btn.classList.add("c-circle--active")
        status = true
      }
      let strength = document.querySelector(".c-circle--active")
      strength = strength.getAttribute("data-strength")
      socket.emit("F2B_switch_manual", {sensor_id: id, status: status, strength: strength})
    })
  }
}

const listenToClickSensors = function(){
  const buttons = document.querySelectorAll(".js-sensor");
  for (const btn of buttons) {
    btn.addEventListener("click", function() {
      const id = btn.getAttribute("data-sensor-id");
      let test = document.querySelector(".c-historiek__btn--active")
      test.classList.remove("c-historiek__btn--active")
      btn.classList.add("c-historiek__btn--active")
      const naam = btn.innerHTML
      currentSensornaam = naam;
      currentSensorid = id;
      getGraph();
    })
  }
}

const listenToClickPeriode = function() {
  const periode = document.querySelectorAll(".js-periode")
  for (const p of periode) {
    p.addEventListener("click", function() {
      let test = document.querySelector(".c-historiek__btn2--active")
      test.classList.remove("c-historiek__btn2--active")
      p.classList.add("c-historiek__btn2--active")
      const naam = p.getAttribute("data-periode-naam");
      currentPeriode = naam
      getGraph();
        
    })
  }
}

const listenToChangeDate = function(){
  html_date.addEventListener("change", function(){
    getGraph();
  })
}
const listenToClickSubMenu = function() {
  const buttons = document.querySelectorAll(".js-btn")
  for (const btn of buttons) {
    btn.addEventListener("click", function() {
      let test = document.querySelector(".c-circle--active-b")
      test.classList.remove("c-circle--active-b")
      btn.classList.add('c-circle--active-b')
      const id = btn.getAttribute("data-sensor-id")
      
      const text = document.querySelectorAll("[data-text-id]")
      for (const t of text) {
        t.classList.add("u-display-none")
      }
      document.querySelector(`[data-text-id="${id}"]`).classList.remove("u-display-none")

    })
  }
}
const listenToClickInfo = function() {
  const buttons = document.querySelectorAll('.js-info-btn')
  for (const btn of buttons) {
    btn.addEventListener("click", function(){
      let test = document.querySelector(".c-circle--active-b")
      test.classList.remove("c-circle--active-b")
      
      const id = btn.getAttribute("data-sensor-id")
      const b = document.querySelector(`.js-btn[data-sensor-id="${id}"]`)
      b.classList.add('c-circle--active-b')
      const text = document.querySelectorAll("[data-text-id]")
      for (const t of text) {
        t.classList.add("u-display-none")
      }
      document.querySelector(`[data-text-id="${id}"]`).classList.remove("u-display-none")
    })
  }
}

const listenToKeyEventTab = function() {
  const buttons = document.querySelectorAll(`[tabindex="0"]`)
  
  for (const btn of buttons){
    btn.addEventListener('keydown', event => {
      if(event.code === 'Space' || event.code === 'Enter') {
        btn.click();
      }
    })
  }
}
//#endregion



//#region ***  INIT / DOMContentLoaded  ***
document.addEventListener("DOMContentLoaded", function () {
  console.info("DOM geladen");


  // Alles van de Pagina Historiek inladen en klaarzetten.
  if(document.querySelector('.c-historiek')){

    html_sensors = document.querySelector('.js-sensors');
    getSensors();

    html_date = document.querySelector('.js-date');
    let today = new Date().toISOString().substr(0, 10);
    html_date.value = today;
    html_date.max = today;

    listenToChangeDate();

    listenToClickPeriode();
  }

  if (document.querySelector(".js-info")) {
    getData();
    listenToClickSubMenu();
  }

  if (document.querySelector(".c-device")) {
    listenToSocket();
    listenToAutomatic();
    listenToManual();
  }


  // Mobile Navigation Menu
  if (document.querySelector('.js-menu')){
    html_menu = document.querySelector('.js-menu');
    

    html_menu.addEventListener("click", function() {
      document.querySelector(".c-header__mobile").classList.add("c-header__mobile--open");
      document.querySelector("html").classList.add("u-scroll");
      document.querySelector("body").classList.add("u-scroll");
      document.querySelector(".c-mobile-menu__open").classList.add("u-display-none");
      document.querySelector(".c-mobile-menu__close").classList.remove("u-display-none");
    })
  }

  if (document.querySelector('.js-close')){
    html_close = document.querySelector('.js-close');

    html_close.addEventListener("click", function() {
      document.querySelector(".c-header__mobile").classList.remove("c-header__mobile--open");
      document.querySelector("html").classList.remove("u-scroll");
      document.querySelector("body").classList.remove("u-scroll");
      document.querySelector(".c-mobile-menu__open").classList.remove("u-display-none");
      document.querySelector(".c-mobile-menu__close").classList.add("u-display-none");
    })
  }


});
//#endregion