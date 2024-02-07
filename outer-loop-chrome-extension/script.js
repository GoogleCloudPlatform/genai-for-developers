document.getElementById("codeForm").addEventListener("submit", function (event) {
    event.preventDefault();
    const userInput = document.getElementById("userInput").value;
    fetchData(userInput);
});

async function fetchData(data) {
    const res = await fetch("https://REGION-PROJECT.cloudfunctions.net/devai", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ data: data })
    });
    const record = await res.json();
    document.getElementById("data").innerHTML = record.data[0].details;
}
