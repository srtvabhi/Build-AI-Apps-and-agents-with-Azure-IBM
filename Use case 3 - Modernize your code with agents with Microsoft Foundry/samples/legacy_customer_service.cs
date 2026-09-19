using System.Collections;

public class CustomerService
{
    public ArrayList GetCustomers()
    {
        ArrayList customers = new ArrayList();
        customers.Add("Contoso");
        customers.Add("Fabrikam");
        return customers;
    }
}
