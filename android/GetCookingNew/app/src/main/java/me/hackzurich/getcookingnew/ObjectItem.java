package me.hackzurich.getcookingnew;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.HashSet;
import java.util.Set;

//another class to handle item's id and name
public class ObjectItem {

  public String itemName;
  public Set<String> eans;
  public boolean bought;
    public int price;
    public Integer id;

    // constructor
  public ObjectItem(int id, String itemName, JSONArray eans, int price) {
      this.id=id;
      this.itemName = itemName;
      this.eans = new HashSet<String>();
      for (int i = 0; i < eans.length(); i++) {
          try {
              this.eans.add(eans.getString(i));
          } catch (JSONException e) {
              e.printStackTrace();
          }
      }
      bought = false;
      this.price=price;
  }

    public ObjectItem(String itemName, String ean1) {
        this.itemName = itemName;
        this.eans = new HashSet<String>();
        this.eans.add(ean1);
        bought = false;
        price=0;
    }

    public void update(JSONObject obj) {
        JSONArray eans = null;
        try {
            this.id=obj.getInt("id");
            this.itemName = obj.getString("title");
            this.price = obj.getInt("price");
            eans = obj.getJSONArray("eans");
            this.eans = new HashSet<String>();
            for (int i = 0; i < eans.length(); i++) {
                try {
                    this.eans.add(eans.getString(i));
                } catch (JSONException e) {
                    e.printStackTrace();
                }
            }
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }
}