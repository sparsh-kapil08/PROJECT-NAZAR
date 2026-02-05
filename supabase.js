import { createClient } from '@supabase/supabase-js'
const supabaseUrl = process.env.SUPABASE;
const supabaseKey = process.env.DB_API_KEY;
try{
    const supabase = createClient(supabaseUrl, supabaseKey);
}
catch(err){
    console.log(err);
    console.log("database error");
}
export default supabase;