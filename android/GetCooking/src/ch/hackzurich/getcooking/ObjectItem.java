package ch.hackzurich.getcooking;

//another class to handle item's id and name
public class ObjectItem {

  public String itemName;
  public String ean;
  public boolean bought;

  // constructor
  public ObjectItem(String itemName, String ean, float price) {
      this.itemName = itemName;
      this.ean = ean;
      bought = false;
  }

}