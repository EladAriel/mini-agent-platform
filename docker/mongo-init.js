try {
    // 1. Switch to the target database
    db_name = process.env.MONGO_INITDB_DATABASE;

    if (!db_name) {
        throw new Error("Database name is missing.");
    }

    db = db.getSiblingDB(db_name);

    // 2. Define the user details
    const appUser = process.env.MONGO_INITDB_APP_USER;
    const appPwd = process.env.MONGO_INITDB_APP_PASSWORD;

    if (!appPwd) {
        throw new Error("Database password is missing.");
    }

    // 3. Cehck if user exists before creating
    const existingUser = db.getUser(appUser);

    if (!existingUser) {
            db.createUser({
                user: appUser,
                pwd: appPwd,
                roles: [
                    {
                        role: "readWrite",
                        db: db.getName()
                    }
                ],
            });

        console.info(`✅ MongoDB init: ${appUser} created with readWrite permissions.`)
    } else {
        console.info(`ℹ️ MongoDB init: User ${appUser} already exists, skipping creation.`)
    }
} catch(error) {
    console.error("❌ MongoDB Initialization Failed!");
    console.error(`Reason: ${error.message}`);
    console.error("👉 Please check your .env file and ensure all MONGODB_ variables are set correctly.");
    throw error;
}