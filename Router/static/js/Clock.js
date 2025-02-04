function updateTime() {
    const options = { timeZoneName: 'short' };
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US');
    const timezoneString = now.toLocaleTimeString('en-US', options).split(' ')[2];

    document.getElementById('time').innerText = timeString;
    document.getElementById('timezone').innerText = timezoneString;
}

setInterval(updateTime, 1000);
window.onload = updateTime;