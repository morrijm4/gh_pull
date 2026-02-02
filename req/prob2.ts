const url = new URL("https://jsonplaceholder.typicode.com");

type ToDoResponse = {
    title: string
}

type Report = {
    quantity: number,
    title: string,
}

type ReportMap = {
    [productId: string]: Report
}

type ShipmentMap = {
    [productId: number]: number
};

async function main() {
    const shipment = [
        { productId: 101, quantity: 5 },
        { productId: 102, quantity: 3 },
        { productId: 101, quantity: 2 }
    ];

    const map = shipment.reduce((acc, { productId, quantity }) => {
        acc[productId] ??= 0;
        acc[productId] += quantity;
        return acc;
    }, {} as ShipmentMap);

    await Promise.all(Object.entries(map).map(async ([productId, quantity]) => {
        try {
            const response = await fetch(new URL('/posts', url), {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: "Update",
                    productId: parseInt(productId),
                    newQuantity: quantity,
                }),
            });

            if (!response.ok) throw new Error("Bad Status Code");
        } catch (e) {
            console.log(`Product ID: ${productId} failed`)
        }
    }));

    const reports: ReportMap = {};

    await Promise.all(Object.entries(map).map(async ([productId, quantity]) => {
        try {
            const response = await fetch(new URL(`/todos/${productId}`, url));
            const body = await response.json() as ToDoResponse;
            reports[productId] = { quantity, title: body.title };
        } catch {
            console.log(`Product ID: ${productId} failed`)
        }
    }));

    console.table(reports);
}

main();
