/********** Timetable Utils **********/

let currentDay = (new Date()).getDay()
if (currentDay > 5) currentDay = 1
if (currentDay < 1) currentDay = 1

let currentType
let currentValue

let isMobile
let isPullToRefreshAllowed = true

razredi.sort()
ucitelji.sort()
ucilnice.sort()

function createTable() {
  document.getElementById('timetable').classList.remove('d-none')
  document.getElementById(`day-${currentDay}`).className += ' day-highlight'

  const timetableBody = document.getElementById('timetable-body')

  for (let time = 0; time <= 8; time++) {
    const rowElement = document.createElement('tr')

    const timeElement = document.createElement('td')
    timeElement.setAttribute('scope', 'row')
    timeElement.className = 'align-middle'
    timeElement.id = `time-${time}`
    timeElement.innerHTML = time === 0 ? 'PU' : `${time}.`
    rowElement.appendChild(timeElement)

    for (let day = 1; day <= 5; day++) {
      const cellElement = document.createElement('td')

      cellElement.className = 'align-middle time-cell' + (day === currentDay ? ' day-highlight' : '')
      if (day !== currentDay) cellElement.className += ' d-none d-lg-table-cell'

      cellElement.id = `${time}-${day}`
      rowElement.appendChild(cellElement)
    }

    timetableBody.appendChild(rowElement)
  }
}

function clearTable() {
  document.getElementById('class-name-desktop').innerHTML = ''
  document.getElementById('class-name-mobile').innerHTML = ''

  document.title = 'Urnik Gimnazije Vič'
  isPullToRefreshAllowed = true

  for (let time = 0; time <= 8; time++) {
    for (let day = 1; day <= 5; day++) {
      const cellElement = document.getElementById(`${time}-${day}`)
      cellElement.innerHTML = ''

      cellElement.classList.remove('substitution-highlight')

      if (day === currentDay) {
        cellElement.classList.remove('d-none')
        cellElement.classList.remove('d-lg-table-cell')
      } else {
        cellElement.classList.add('d-none')
        cellElement.classList.add('d-lg-table-cell')
      }
    }

    const rowElement = document.getElementById(`time-${time}`)
    rowElement.classList.remove('substitution-highlight')
  }

  document.getElementById('timetable').classList.remove('d-none')
  document.getElementById('not-settings').classList.remove('d-none')
  document.getElementById('not-found-message').classList.add('d-none')
  document.getElementById('settings').classList.add('d-none')
}

function refreshTable(forceViewSwitch = true) {
  if (!forceViewSwitch && window.location.pathname === '/settings') return

  if (currentType === 'class') fillClassData(currentValue)
  else if (currentType === 'teacher') fillTeacherData(currentValue)
  else if (currentType === 'classroom') fillClassroomData(currentValue)
}

function fillClassData(className) {
  clearTable()

  for (const classN of className) {
    if (!razredi.includes(classN)) {
      router.resolve('not-found')
      return
    }
  }

  const enablelinks = document.getElementById('enable-links-in-timetable').checked

  currentType = 'class'
  currentValue = className

  router.pause()
  router.navigate(`/classes/${className.join(',')}`)
  router.resume()

  document.getElementById('class-name-desktop').innerHTML = className.join(', ')
  document.getElementById('class-name-mobile').innerHTML = ` – ${className.join(', ')}`

  document.title = `Urnik Gimnazije Vič – ${className.join(', ')}`

  let data = {}

  for (let i = 0; i < podatki.length; i++) {
    if (className.includes(podatki[i][1])) {
      const timeId = `${podatki[i][6]}-${podatki[i][5]}`

      const subject = podatki[i][3]
      const teacher = enablelinks ? `<a href="/teachers/${podatki[i][2]}">${podatki[i][2]}</a>` : podatki[i][2]
      const classroom = enablelinks ? `<a href="/classrooms/${podatki[i][4]}">${podatki[i][4]}</a>` : podatki[i][4]

      if (!(timeId in data)) data[timeId] = {
        subjects: [],
        teachers: [],
        classrooms: [],
      }

      if (subject && !data[timeId].subjects.includes(subject)) data[timeId].subjects.push(subject)
      if (podatki[i][2] && !data[timeId].teachers.includes(teacher)) data[timeId].teachers.push(teacher)
      if (podatki[i][4] && !data[timeId].classrooms.includes(classroom)) data[timeId].classrooms.push(classroom)
    }
  }

  if (document.getElementById('show-substitutions').checked) {
    const substitutions = getSubstitutions()
    for (const classN of className) {
      for (const time in data) {
        const substitutionId = `${classN}-${time}`
        if (substitutions[substitutionId]) {
          const substitution = substitutions[substitutionId]
          const timeId = substitutionId.replace(`${classN}-`, '')

          substitution.ucitelj = substitution.ucitelj.split(' ')[0].replace(/ć/g, 'č')

          const subject = substitution.predmet
          const teacher = enablelinks ? `<a href="/teachers/${substitution.ucitelj}">${substitution.ucitelj}</a>` : substitution.ucitelj
          const classroom = enablelinks ? `<a href="/classrooms/${substitution.ucilnica}">${substitution.ucilnica}</a>` : substitution.ucilnica

          const cellElement = document.getElementById(time)
          cellElement.classList.add('substitution-highlight')

          if (isMobile && parseInt(time.split('-')[1]) === currentDay) {
            const rowElement = document.getElementById(`time-${time.split('-')[0]}`)
            rowElement.classList.add('substitution-highlight')
          }

          if (substitution.predmet) {
            data[timeId] = {
              subjects: [subject],
              teachers: [teacher],
              classrooms: [classroom]
            }
          } else {
            delete data[timeId]
          }
        }
      }
    }
  }

  for (const time in data) {
    const cellElement = document.getElementById(time)

    const cellData = [
      data[time].subjects.join('/'),
      data[time].teachers.join('/'),
      data[time].classrooms.join('/')
    ].filter(e => e)

    if (isMobile) cellElement.innerHTML = '<div><div>' + cellData.join('</div><div>') + '</div></div>'
    else cellElement.innerHTML = cellData.join(' - ')
  }
}

function fillTeacherData(teacherName) {
  clearTable()

  for (const teacher of teacherName) {
    if (!ucitelji.includes(teacher)) {
      router.resolve('not-found')
      return
    }
  }

  currentType = 'teacher'
  currentValue = teacherName

  router.pause()
  router.navigate(`/teachers/${teacherName.join(',')}`)
  router.resume()

  document.getElementById('class-name-desktop').innerHTML = teacherName.join(', ')
  document.getElementById('class-name-mobile').innerHTML = ` – ${teacherName.join(', ')}`

  document.title = `Urnik Gimnazije Vič – ${teacherName.join(', ')}`

  let data = {}

  for (let i = 0; i < podatki.length; i++) {
    if (teacherName.includes(podatki[i][2])) {
      const timeId = `${podatki[i][6]}-${podatki[i][5]}`

      const classN = `<a href="/classes/${podatki[i][1]}">${podatki[i][1]}</a>`
      const subject = podatki[i][3]
      const classroom = `<a href="/classrooms/${podatki[i][4]}">${podatki[i][4]}</a>`

      if (!(timeId in data)) data[timeId] = {
        classes: [],
        subjects: [],
        classrooms: [],
      }

      if (podatki[i][1] && !data[timeId].classes.includes(classN)) data[timeId].classes.push(classN)
      if (subject && !data[timeId].subjects.includes(subject)) data[timeId].subjects.push(subject)
      if (podatki[i][4] && !data[timeId].classrooms.includes(classroom)) data[timeId].classrooms.push(classroom)
    }
  }

  for (const time in data) {
    const cellElement = document.getElementById(time)

    const cellData = [
      data[time].classes.join('/'),
      data[time].subjects.join('/'),
      data[time].classrooms.join('/')
    ].filter(e => e)

    if (isMobile) cellElement.innerHTML = '<div><div>' + cellData.join('</div><div>') + '</div></div>'
    else cellElement.innerHTML = cellData.join(' - ')
  }
}

function fillClassroomData(classroomName) {
  clearTable()

  if (classroomName.includes('empty')) {
    fillEmptyClassrooms()
    return
  }

  for (const classroom of classroomName) {
    if (!ucilnice.includes(classroom)) {
      router.resolve('not-found')
      return
    }
  }

  currentType = 'classroom'
  currentValue = classroomName

  router.pause()
  router.navigate(`/classrooms/${classroomName.join(',')}`)
  router.resume()

  document.getElementById('class-name-desktop').innerHTML = classroomName.join(', ')
  document.getElementById('class-name-mobile').innerHTML = ` – ${classroomName.join(', ')}`

  document.title = `Urnik Gimnazije Vič – ${classroomName.join(', ')}`

  let data = {}

  for (let i = 0; i < podatki.length; i++) {
    if (classroomName.includes(podatki[i][4])) {
      const timeId = `${podatki[i][6]}-${podatki[i][5]}`

      const classN = `<a href="/classes/${podatki[i][1]}">${podatki[i][1]}</a>`
      const subject = podatki[i][3]
      const teacher = `<a href="/teachers/${podatki[i][2]}">${podatki[i][2]}</a>`

      if (!(timeId in data)) data[timeId] = {
        classes: [],
        subjects: [],
        teachers: [],
      }

      if (podatki[i][1] && !data[timeId].classes.includes(classN)) data[timeId].classes.push(classN)
      if (subject && !data[timeId].subjects.includes(subject)) data[timeId].subjects.push(subject)
      if (podatki[i][2] && !data[timeId].teachers.includes(teacher)) data[timeId].teachers.push(teacher)
    }
  }

  for (const time in data) {
    const cellElement = document.getElementById(time)

    const cellData = [
      data[time].classes.join('/'),
      data[time].subjects.join('/'),
      data[time].teachers.join('/')
    ].filter(e => e)

    if (isMobile) cellElement.innerHTML = '<div><div>' + cellData.join('</div><div>') + '</div></div>'
    else cellElement.innerHTML = cellData.join(' - ')
  }
}

function fillEmptyClassrooms() {
  currentType = 'classroom'
  currentValue = 'empty'

  router.pause()
  router.navigate('/classrooms/empty')
  router.resume()

  document.getElementById('class-name-desktop').innerHTML = 'Proste učilnice'
  document.getElementById('class-name-mobile').innerHTML = ' – Proste učilnice'

  document.title = 'Urnik Gimnazije Vič – Proste učilnice'

  for (let day = 1; day <= 5; day++) {
    for (let time = 0; time <= 8; time++) {
      let emptyClassrooms = []

      for (let classroom = 0; classroom < ucilnice.length; classroom++) {
        if (['TV1', 'TV2', 'TV3'].includes(ucilnice[classroom])) continue

        let isEmpty = true
        for (let i = 0; i < podatki.length; i++) {
          if (podatki[i][5] === day && podatki[i][6] === time && podatki[i][4] === ucilnice[classroom]) {
            isEmpty = false
            break
          }
        }

        if (isEmpty) emptyClassrooms.push(`<a href="/classrooms/${ucilnice[classroom]}">${ucilnice[classroom]}</a>`)
      }

      const cellElement = document.getElementById(`${time}-${day}`)
      cellElement.innerHTML = emptyClassrooms.sort().join(' - ')
    }
  }
}

// TODO: Step 1: Better UI
// Hide lines where whole line for the whole week is empty (on desktop)
// Hide cells where cell for current day is empty (on mobile)

// TODO: Step 3: More features
// Display menu and lunch schedule
// Display all announcements and substitutions as link

// TODO Step 4: Make those features even better
// Use https://pdfobject.com/ (detection) with PDF.js (display) for PDF files
// Use cloudconvert.com to convert DOCX files to PDF and display them

/********** Substitutions Utils **********/

let substitutionsAPI = 'https://api.gimvicurnik.filips.si/nad?dan='

function getMonday(date) {
  date = new Date(date)

  let day = date.getDay()
  let diff = date.getDate() - day + 1

  if (day === 6) diff = date.getDate() + 2
  if (day === 0) diff = date.getDate() + 1

  return new Date(date.setDate(diff))
}

function getWeekDays(monday) {
  let days = {}

  for (let i = 0; i < 5; i++) {
    days[i + 1] = new Date(monday.getTime() + i * (24 * 60 * 60 * 1000))
  }

  return days
}

function getSubstitutionId(substitution) {
  // TODO: Step 2: Support for edge cases (izbirni predmeti, polovica razreda, projektno delo, menjave iz ene učilnice v isto učilnico ...)
  // Make PDF parsing better and more reliable (needs change only on API)
  // Use original teacher as additional key (also needs change on API)
  return substitution.razred.split(' - ')[0] + '-' + substitution.ura + '-' + new Date(substitution.dan).getDay()
}

async function updateSubstitutions() {
  let weekDays = getWeekDays(getMonday(new Date()))
  let data = {}

  let cachedData = {}
  if (window.localStorage && window.localStorage.getItem('substitutions-storage')) {
    cachedData = JSON.parse(window.localStorage.getItem('substitutions-storage') || '{}')
  }

  for (const [day, date] of Object.entries(weekDays)) {
    let dateISO = date.toISOString().split('T')[0]

    let currentData = []
    let currentCachedData = cachedData[dateISO]

    try {
      const currentURL = substitutionsAPI + dateISO
      const response = await fetch(currentURL)
      currentData = await response.json()

    } catch (error) {
      if (currentCachedData) {
        currentData = currentCachedData
      }
    }

    data[dateISO] = currentData
  }

  if (window.localStorage) window.localStorage.setItem('substitutions-storage', JSON.stringify(data))
  return data
}

function getSubstitutions() {
  let cachedData = {}
  if (window.localStorage && window.localStorage.getItem('substitutions-storage')) {
    cachedData = JSON.parse(window.localStorage.getItem('substitutions-storage') || '{}')
  }

  return Object.values(cachedData)
    .flat()
    .reduce((obj, item) => (obj[getSubstitutionId(item)] = item, obj) ,{})
}

/********** Mobile Detection **********/

isMobile = window.innerWidth < 992
window.onresize = () => {
  if (isMobile && window.innerWidth >= 992) {
    isMobile = false
    refreshTable()
  } else if (!isMobile && window.innerWidth < 992) {
    isMobile = true
    updateMagicLine()
    refreshTable()
  }
}

/********** Mobile Navigation **********/

function easeInOutQuad(t, b, c, d) {
  t /= d/2
  if (t < 1) return c/2*t*t + b
  t--
  return -c/2 * (t*(t-2) - 1) + b
}

function scrollToAnimated(element, to, duration) {
  const start = element.scrollLeft
  const change = to - start

  let currentTime = 0
  let increment = 1

  const animateScroll = (resolve) => {
    currentTime += increment
    element.scrollLeft = easeInOutQuad(currentTime, start, change, duration)
    if (currentTime < duration) setTimeout(() => animateScroll(resolve), increment)
    else resolve()
  }

  return new Promise(resolve => animateScroll(resolve))
}

const daySwitcher = document.getElementById('day-switcher')
const magicLine = document.getElementById('magic-line')

let supportsAnimations = true
if (typeof magicLine.animate === 'undefined') supportsAnimations = false

let supportsMagicLine = true
if (navigator.vendor === 'Apple Computer, Inc.') supportsMagicLine = false

daySwitcher.scrollLeftMax = daySwitcher.scrollLeftMax || daySwitcher.scrollWidth - daySwitcher.clientWidth
magicLine.animate = magicLine.animate || function () {
  this.callback = function () {}

  setTimeout(() => this.callback.onfinish(), 5)
  return this.callback
}

let isChangingDay = false

for (let link of document.getElementsByClassName('nav-link')) {
  link.onclick = event => {
    let boundingRect = event.target.getBoundingClientRect()

    try { document.getElementsByClassName('nav-link active')[0].classList.remove('active') }
    catch (error) {}

    document.getElementById('magic-line').classList.remove('d-none')
    event.target.classList.add('active')

    currentDay = parseInt(link.id.replace('day-switcher-', ''))
    refreshTable()

    let newScrollPosition = Math.min(Math.max(boundingRect.left, 0), daySwitcher.scrollLeftMax)
    let scrollPositionChange = daySwitcher.scrollLeft - newScrollPosition
    let newLeftPosition = boundingRect.left + scrollPositionChange

    if (supportsAnimations) {
      isChangingDay = true
      scrollToAnimated(daySwitcher, boundingRect.left, 50).then(() => {
        isChangingDay = false
      })

    } else {
      isChangingDay = true
      daySwitcher.scrollLeft = boundingRect.left
      setTimeout(() => isChangingDay = false, 5)
    }

    if (!supportsMagicLine) return

    magicLine.animate([{
      width: boundingRect.width + 'px',
      left: newLeftPosition  + 'px'
    }], {
      duration: 100
    }).onfinish = () => {
      magicLine.style.width = boundingRect.width + 'px'
      magicLine.style.left = newLeftPosition  + 'px'
    }
  }
}

document.getElementById(`day-switcher-${currentDay}`).classList.add('active')

let activeTab = document.getElementsByClassName('nav-link active')[0]
let activeBoundingRect = activeTab.getBoundingClientRect()
daySwitcher.scrollLeft = activeBoundingRect.left

if (supportsMagicLine) {
  updateMagicLine()
} else {
  const style = document.createElement('style')
  style.innerHTML = '.nav-link.active { font-weight: 600; }'
  document.head.appendChild(style)
}

daySwitcher.onscroll = () => {
  if (isChangingDay || !supportsMagicLine) return
  activeBoundingRect = activeTab.getBoundingClientRect()

  let newWidth = activeBoundingRect.width
  newWidth -= Math.max(activeBoundingRect.x + newWidth - window.innerWidth, 0)

  activeTab = document.getElementsByClassName('nav-link active')[0]
  activeBoundingRect = activeTab.getBoundingClientRect()
  magicLine.style.width = newWidth + 'px'
  magicLine.style.left = activeBoundingRect.left + 'px'
}

function updateMagicLine() {
  activeTab = document.getElementsByClassName('nav-link active')[0]
  activeBoundingRect = activeTab.getBoundingClientRect()

  magicLine.style.width = activeBoundingRect.width + 'px'
  magicLine.style.left = activeBoundingRect.left + 'px'
  magicLine.style.top = activeBoundingRect.top + activeBoundingRect.height - 2 + 'px'
  magicLine.style.display = 'block'
}

/********** Pull to Refresh **********/

const ptr = PullToRefresh.init({
  mainElement: '#main',
  triggerElement: 'body',

  instructionsPullToRefresh: 'Povlečite za posodobitev',
  instructionsReleaseToRefresh: 'Izpustite za posodobitev',
  instructionsRefreshing: 'Posodabljanje',

  shouldPullToRefresh: () => !window.scrollY && isPullToRefreshAllowed && document.getElementById('enable-pull-to-refresh').checked,
  onRefresh: updateData
})

/********** Cache Controls **********/

function updateEverything() {
  if (!window.navigator.onLine) {
    $('.toast').toast('show')
    return
  }

  try {
    const cacheClearRequestsChannel = new MessageChannel()
    navigator.serviceWorker.controller.postMessage({
      action: 'clear-cache-all'
    }, [cacheClearRequestsChannel.port2])
  } catch (error) {
    console.error(error)
    const cacheUpdatesChannel = new BroadcastChannel('cache-updates')
    cacheUpdatesChannel.postMessage({date: new Date(), refreshAll: true})
  }

}

function updateData() {
  if (!window.navigator.onLine) {
    $('.toast').toast('show')
    return
  }

  try {
    const cacheClearRequestsChannel = new MessageChannel()
    navigator.serviceWorker.controller.postMessage({
      action: 'clear-cache-data'
    }, [cacheClearRequestsChannel.port2])
  } catch (error) {
    console.error(error)
    const cacheUpdatesChannel = new BroadcastChannel('cache-updates')
    cacheUpdatesChannel.postMessage({date: new Date(), refreshData: true})
  }
}

if (window.localStorage) {
  document.getElementById('last-updated').innerHTML = window.localStorage.getItem('last-updated')

  document.getElementById('show-substitutions').checked = parseInt(window.localStorage.getItem('show-substitutions') || 1)
  document.getElementById('enable-pull-to-refresh').checked = parseInt(window.localStorage.getItem('enable-pull-to-refresh') || 1)
  document.getElementById('enable-links-in-timetable').checked = parseInt(window.localStorage.getItem('enable-links-in-timetable') || 1)
}

const cacheUpdatesChannel = new BroadcastChannel('cache-updates')
cacheUpdatesChannel.addEventListener('message', event => {
  if (typeof event.data.date === 'string') event.data.date = new Date(event.data.date)

  const date = event.data.date.toLocaleDateString('sl-SI', {hour: 'numeric', minute: 'numeric'})
  document.getElementById('last-updated').innerHTML = date
  if (window.localStorage) window.localStorage.setItem('last-updated', date)

  if (event.data.refreshAll) {
    updateSubstitutions()
    window.location = location.protocol + '//' + location.host + '?updated=' + event.data.date.getTime()
  }

  if (event.data.refreshData) {
    document.getElementById('data-provider').remove()

    const dataProvider = document.createElement('script')
    dataProvider.id = 'data-provider'
    dataProvider.src = '/js/data.js?updated=' + event.data.date.getTime()

    dataProvider.onreadystatechange = dataProvider.onload = async (event) => {
      router._lastRouteResolved.url = '/nothing'
      await updateSubstitutions()
      refreshTable()
    }

    document.body.appendChild(dataProvider)
  }
})

/********** Class Selection **********/

let classSelectionStage = false

function displaySelectionModal(firstTime = false) {
  classSelectionStage = {firstTime: firstTime}
  isPullToRefreshAllowed = false
  let options

  if (firstTime) {
    classSelectionStage.view = 'welcome'

    document.getElementById('class-selection-modal-close').classList.add('d-none')
    document.getElementById('class-selection-modal-logo').classList.remove('d-none')
    document.getElementById('class-selection-modal').classList.remove('fade')
    document.getElementById('class-selection-modal').classList.add('modal-fullscreen')
    options = {backdrop: 'static', keyboard: false}

    document.getElementById('class-selection-modal-title').innerHTML = 'Aplikacija GimVič'
    document.getElementById('first-time').classList.remove('d-none')
    document.getElementById('type-selection').classList.add('d-none')
    document.getElementById('value-selection').classList.add('d-none')

  } else {
    classSelectionStage.view = 'type'

    document.getElementById('class-selection-modal-close').classList.remove('d-none')
    document.getElementById('class-selection-modal-logo').classList.add('d-none')
    document.getElementById('class-selection-modal').classList.add('fade')
    document.getElementById('class-selection-modal').classList.remove('modal-fullscreen')
    options = {backdrop: true, keyboard: true}

    document.getElementById('class-selection-modal-title').innerHTML = 'Izberite pogled'
    document.getElementById('first-time').classList.add('d-none')
    document.getElementById('type-selection').classList.remove('d-none')
    document.getElementById('value-selection').classList.add('d-none')
  }

  $('#class-selection-modal').removeData().off().modal(options)
  history.pushState(null, null)
}

document.getElementById('confirm-first-time').onclick = () => {
  classSelectionStage.view = 'type'

  document.getElementById('class-selection-modal-title').innerHTML = 'Izberite pogled'
  document.getElementById('first-time').classList.add('d-none')
  document.getElementById('type-selection').classList.remove('d-none')
}

document.getElementById('class-selection-class').onclick = () => {
  history.pushState(null, null)
  classSelectionStage.view = 'value'

  document.getElementById('class-selection-modal-title').innerHTML = 'Izberite razred in izbirne predmete'
  document.getElementById('type-selection').classList.add('d-none')
  document.getElementById('value-selection').classList.remove('d-none')

  const selectElement = document.getElementById('value-selection-select')
  selectElement.innerText = null
  const labelOption = new Option('Izberite razred ...', null, true, true)
  labelOption.disabled = true
  selectElement.add(labelOption)
  for (let classN of razredi) selectElement.add(new Option(classN))

  selectElement.multiple = true
  selectElement.size = Math.min(10, razredi.length)
  if (/Android.+Firefox\//.test(navigator.userAgent)) selectElement.size = Math.min(5, razredi.length)

  selectElement.onchange = () => {
    if (selectElement.selectedOptions.length > 1) {
      for (const selectedOption of selectElement.selectedOptions) {
        if (selectedOption.value === 'null') selectedOption.selected = false
      }
    }
  }

  document.getElementById('value-selection-submit').onclick = () => {
    const shouldStore = document.getElementById('value-selection-should-store').checked
    if (!selectElement.checkValidity()) return

    saveChoice('class', Array.prototype.map.call(selectElement.selectedOptions, option => option.value), shouldStore)
    history.pushState(null, null)
    classSelectionStage = false
  }
}

document.getElementById('class-selection-teacher').onclick = () => {
  history.pushState(null, null)
  classSelectionStage.view = 'value'

  document.getElementById('class-selection-modal-title').innerHTML = 'Izberite profesorja'
  document.getElementById('type-selection').classList.add('d-none')
  document.getElementById('value-selection').classList.remove('d-none')

  const selectElement = document.getElementById('value-selection-select')
  selectElement.innerText = null
  selectElement.multiple = false
  selectElement.size = 1
  const labelOption = new Option('Izberite profesorja ...', null, true, true)
  labelOption.disabled = true
  selectElement.add(labelOption)
  for (let teacher of ucitelji) selectElement.add(new Option(teacher))

  document.getElementById('value-selection-submit').onclick = () => {
    const shouldStore = document.getElementById('value-selection-should-store').checked
    if (!selectElement.checkValidity()) return

    saveChoice('teacher', Array.prototype.map.call(selectElement.selectedOptions, option => option.value), shouldStore)
    history.pushState(null, null)
    classSelectionStage = false
  }
}

document.getElementById('class-selection-classroom').onclick = () => {
  history.pushState(null, null)
  classSelectionStage.view = 'value'

  document.getElementById('class-selection-modal-title').innerHTML = 'Izberite učilnico'
  document.getElementById('type-selection').classList.add('d-none')
  document.getElementById('value-selection').classList.remove('d-none')

  const selectElement = document.getElementById('value-selection-select')
  selectElement.innerText = null
  selectElement.multiple = false
  selectElement.size = 1
  const labelOption = new Option('Izberite učilnico ...', null, true, true)
  labelOption.disabled = true
  selectElement.add(labelOption)
  selectElement.add(new Option('Proste učilnice', 'empty'))
  for (let classroom of ucilnice) selectElement.add(new Option(classroom))

  document.getElementById('value-selection-submit').onclick = () => {
    const shouldStore = document.getElementById('value-selection-should-store').checked
    if (!selectElement.checkValidity()) return

    saveChoice('classroom', Array.prototype.map.call(selectElement.selectedOptions, option => option.value), shouldStore)
    history.pushState(null, null)
    classSelectionStage = false
  }
}

function saveChoice(type, value, store = true) {
  document.getElementById('day-switcher').classList.remove('d-none')
  $('#class-selection-modal').modal('hide')

  value = value.filter(option => option !== 'null')

  routeTypes(false, type, value)

  if (window.localStorage && store) {
    window.localStorage.setItem('current-type', type)
    window.localStorage.setItem('current-value', JSON.stringify(value))
  }
}

/********** Single Page Routing **********/

function routeTypes(useStorage, currentType, currentValue) {
  if (window.localStorage && useStorage) {
    currentType = window.localStorage.getItem('current-type')
    currentValue = JSON.parse(window.localStorage.getItem('current-value') || '[]')
  }

  if (currentType === 'class') {
    router.navigate(`/classes/${currentValue}`, true)
    return true
  } else if (currentType === 'teacher') {
    router.navigate(`/teachers/${currentValue}`, true)
    return true
  } else if (currentType === 'classroom') {
    router.navigate(`/classrooms/${currentValue}`, true)
    return true
  }

  return false
}

function handleSettings() {
  document.getElementById('class-name-desktop').innerHTML = 'Nastavitve'
  document.getElementById('class-name-mobile').innerHTML = ' – Nastavitve'

  document.title = 'Urnik Gimnazije Vič – Nastavitve'
  isPullToRefreshAllowed = false

  document.getElementById('timetable').classList.add('d-none')
  document.getElementById('not-settings').classList.add('d-none')
  document.getElementById('not-found-message').classList.add('d-none')
  document.getElementById('settings').classList.remove('d-none')

  document.getElementById('magic-line').classList.add('d-none')
  try { document.getElementsByClassName('nav-link active')[0].classList.remove('active') }
  catch (error) {}

  if (window.localStorage) {
    currentType = window.localStorage.getItem('current-type')
    currentValue = JSON.parse(window.localStorage.getItem('current-value') || '[]')
  }

  let currentClassLabel
  if (currentType === 'class') currentClassLabel = 'Izbran razred'
  if (currentType === 'teacher') currentClassLabel = 'Izbran profesor'
  if (currentType === 'classroom') currentClassLabel = 'Izbrana učilnica'

  let currentClassValue = currentValue.join(', ')
  if (currentClassValue === 'empty') currentClassValue = 'Proste učilnice'

  document.getElementById('class-name-settings-label').innerHTML = currentClassLabel
  document.getElementById('class-name-settings').innerHTML = currentClassValue

  document.getElementById('last-updated-settings').innerHTML = document.getElementById('last-updated').innerHTML

  document.getElementById('update-everything').onclick = updateEverything
  document.getElementById('update-data').onclick = updateData

  document.getElementById('show-substitutions').onclick = () => {
    if (window.localStorage) {
      window.localStorage.setItem('show-substitutions', document.getElementById('show-substitutions').checked ? '1' : '0')
    }
  }

  document.getElementById('enable-pull-to-refresh').onclick = () => {
    if (window.localStorage) {
      window.localStorage.setItem('enable-pull-to-refresh', document.getElementById('enable-pull-to-refresh').checked ? '1' : '0')
    }
  }

  document.getElementById('enable-links-in-timetable').onclick = () => {
    if (window.localStorage) {
      window.localStorage.setItem('enable-links-in-timetable', document.getElementById('enable-links-in-timetable').checked ? '1' : '0')
    }
  }

  document.getElementById("select-class").onclick = () => {
    displaySelectionModal()
  }
}

function handleMain() {
  if (!routeTypes(true)) {
    document.getElementById('timetable').classList.add('d-none')
    document.getElementById('not-settings').classList.add('d-none')
    document.getElementById('not-found-message').classList.add('d-none')
    document.getElementById('day-switcher').classList.add('d-none')
    document.getElementById('settings').classList.add('d-none')

    document.getElementById('magic-line').classList.add('d-none')
    try { document.getElementsByClassName('nav-link active')[0].classList.remove('active') }
    catch (error) {}

    displaySelectionModal(true)
  }
}

function handleNotFound() {
  document.getElementById('class-name-desktop').innerHTML = ''
  document.getElementById('class-name-mobile').innerHTML = ''

  document.title = 'Urnik Gimnazije Vič – Stran ni najdena'

  document.getElementById('timetable').classList.add('d-none')
  document.getElementById('not-found-message').classList.remove('d-none')
  document.getElementById('not-settings').classList.remove('d-none')
}

createTable()
updateSubstitutions().then(() => {
  refreshTable(false)
})

const router = new Navigo(`${window.location.protocol}//${window.location.hostname}/`)
router
  .on('classes/:class', params => fillClassData(params.class.split(',')))
  .on('teachers/:teacher', params => fillTeacherData(params.teacher.split(',')))
  .on('classrooms/:classroom', params => fillClassroomData(params.classroom.split(',')))
  .on('settings', handleSettings)
  .on(handleMain)
  .notFound(handleNotFound)
router.resolve()

window.onclick = function(event) {
  const target = event.target.closest('a')
  if (!target) return

  const href = target.getAttribute('href')
  if (!href || href[0] !== '/') return

  router.navigate(href, true)
  event.preventDefault()
}

window.onpopstate = (event) => {
  if (classSelectionStage) {
    if (classSelectionStage.view === 'value') {
      document.getElementById('class-selection-modal-title').innerHTML = 'Izberite pogled'
      document.getElementById('first-time').classList.add('d-none')
      document.getElementById('type-selection').classList.remove('d-none')
      document.getElementById('value-selection').classList.add('d-none')

      classSelectionStage.view = 'type'
      event.preventDefault()
      return

    } else if (classSelectionStage.view === 'type' && classSelectionStage.firstTime === true) {
      document.getElementById('class-selection-modal-title').innerHTML = 'Aplikacija GimVič'
      document.getElementById('first-time').classList.remove('d-none')
      document.getElementById('type-selection').classList.add('d-none')
      document.getElementById('value-selection').classList.add('d-none')

      classSelectionStage.view = 'welcome'
      event.preventDefault()
      return

    } else if (classSelectionStage.view === 'type' && classSelectionStage.firstTime === false) {
      document.getElementById('day-switcher').classList.remove('d-none')
      $('#class-selection-modal').modal('hide')

      classSelectionStage = false
      event.preventDefault()
      return

    } else {
      history.back()
      return
    }
  }

  router.resolve()
}
