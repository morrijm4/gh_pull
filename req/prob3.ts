const url = "https://jsonplaceholder.typicode.com"

interface ToDo {
    completed: boolean
};

interface BasicInfo {
    name: string;
    email: string;
};

interface User {
    name: string;
    email: string;
    taskCount: number;
    status: "Power User" | "Standard";
};

async function fetchBasicInfo(userId: number): Promise<BasicInfo> {
    const response = await fetch(new URL(`/users/${userId}`, url));
    return await response.json() as BasicInfo;
}

async function fetchTodos(userId: number): Promise<ToDo[]> {
    const todoUrl = new URL("/todos", url);
    todoUrl.searchParams.set("userId", userId.toString());

    const response = await fetch(todoUrl);
    return await response.json() as ToDo[];
}

function sanatize({ email, ...rest }: User): Omit<User, 'email'> {
    return rest;
}

async function fetchUser(userId: number): Promise<User> {
    const [{ name, email }, todos] = await Promise.all([
        fetchBasicInfo(userId),
        fetchTodos(userId),
    ]);

    return {
        name,
        email,
        taskCount: todos.length,
        status: todos.filter(todo => todo.completed).length > 5 ? "Power User" : "Standard",
    };
}

async function main() {
    const user = await fetchUser(1);
    console.log(sanatize(user));
}

main();
