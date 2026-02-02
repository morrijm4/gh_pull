interface User {
    id: number;
    name: string;
    username: string;
    address: Address;
    company: Company;
};

interface Address {
    suite: string;
};

interface Company {
    name: string;
    catchPhrase: string;
    bs: string;
};

interface Post {
    body: string
}

const url = new URL("https://jsonplaceholder.typicode.com");

function cmpStrings(a: string, b: string): number {
    a = a.toLowerCase();
    b = b.toLowerCase();

    const n = a.length < b.length ? a.length : b.length;

    for (let i = 0; i < n; i++) {
        if (a[i]! > b[i]!) return 1;
        if (a[i]! < b[i]!) return -1;
    }

    if (a.length > b.length) return -1;
    if (a.length < b.length) return 1;
    return 0;
}

async function main() {
    const response = await fetch(new URL('/users', url));
    const body = await response.json() as User[];
    const users = body.filter((user) => user.address.suite.includes("Suite"))
        .sort((a, b) => cmpStrings(a.username, b.username))

    await Promise.all(users.map(async (user) => {
        const postsUrl = new URL('/posts', url);
        postsUrl.searchParams.set("userId", user.id.toString())
        const res = await fetch(postsUrl);
        const posts = await res.json() as Post[]

        let sum = 0;
        for (const post of posts) {
            sum += post.body.length;
        }

        console.log(user.id, user.username, sum / posts.length)
    }));
}

main();
