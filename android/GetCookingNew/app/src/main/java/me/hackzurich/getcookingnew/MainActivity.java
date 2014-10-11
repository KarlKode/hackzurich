package me.hackzurich.getcookingnew;


import me.hackzurich.getcookingnew.DataLoader.IngredientNameListener;
import me.hackzurich.getcookingnew.DataLoader.ShoppingListLoaderListener;

import android.content.Intent;
import android.graphics.Color;
import android.graphics.LightingColorFilter;
import android.graphics.PorterDuff;
import android.os.Bundle;
import android.support.v4.widget.SwipeRefreshLayout;
import android.support.v4.widget.SwipeRefreshLayout.OnRefreshListener;
import android.support.v7.app.ActionBarActivity;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

public class MainActivity extends ActionBarActivity implements OnRefreshListener {


    private SwipeRefreshLayout mSwipeLayout;
    private ListView mListViewItems;
    private ArrayAdapterItem mAdapter;

    public static int REQUEST_SCAN = 1;
    private TextView totalView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

		/*Intent intent = new Intent(this, LoginActivity.class);
        startActivity(intent);*/


        setContentView(R.layout.activity_main);
		/*if (savedInstanceState == null) {
			getSupportFragmentManager().beginTransaction()
					.add(R.id.container, new MainFragment()).commit();
		}*/


        mSwipeLayout = (SwipeRefreshLayout) findViewById(R.id.swipe_container);
        mSwipeLayout.setOnRefreshListener(this);
        mSwipeLayout.setColorSchemeColors(Color.RED, Color.GREEN, Color.BLUE, Color.CYAN);


        // add your items, this can be done programatically
        // your items can be from a database
        ObjectItem[] ObjectItemData = new ObjectItem[0];

        // our adapter instance
        mAdapter = new ArrayAdapterItem(this, R.layout.list_view_row_item, ObjectItemData);

        // create a new ListView, set the adapter and item click listener
        mListViewItems = (ListView) findViewById(R.id.listView1);
        mListViewItems.setAdapter(mAdapter);
        //listViewItems.setOnItemClickListener(new OnItemClickListenerListViewItem());

        Button btnScan = (Button) findViewById(R.id.buttonScan);
        totalView = (TextView) findViewById(R.id.textViewTotal);


        btnScan.setOnClickListener(new OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(MainActivity.this, ScanActivity.class);
                startActivityForResult(intent, REQUEST_SCAN);
            }
        });


        Button btnCheckout = (Button) findViewById(R.id.buttoncheckout);
        btnCheckout.getBackground().setColorFilter(new LightingColorFilter(0xFFFFFFFF, 0xFFAA0000));
        btnCheckout.setOnClickListener(new OnClickListener() {
            @Override
            public void onClick(View v) {
                checkout();
            }
        });
        doRefresh();
    }

    private void checkout() {
        JSONArray items = new JSONArray();
        for (ObjectItem item : mAdapter.data) {
            if (item.bought) {
                try {
                    JSONObject jo = new JSONObject();
                    jo.put("ean", item.ean);
                    items.put(jo);
                } catch (JSONException e) {
                    e.printStackTrace();
                }
            }
        }
        DataLoader dl = new DataLoader();
        mSwipeLayout.setRefreshing(true);
        dl.buyItems(new DataLoader.DoneListener() {
            @Override
            public void onDone() {

                doRefresh();
            }
        }, items);
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();
        if (id == R.id.action_settings) {
            return true;
        }
        return super.onOptionsItemSelected(item);
    }

    @Override
    public void onRefresh() {
        doRefresh();
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if (resultCode == RESULT_OK && requestCode == REQUEST_SCAN) {
            mSwipeLayout.setRefreshing(true);
            String ean = data.getStringExtra("cleanedBarcode");
            if (!mAdapter.checkByEAN(ean)) {

                ObjectItem obj = new ObjectItem(ean, ean);
                obj.bought = true;
                mAdapter.addObject(obj);
                mAdapter.notifyDataSetChanged();
                totalView.setText("Total: " + mAdapter.getTotal());
                //doRefresh();
            }
//			DataLoader dl = new DataLoader();
//			dl.getIngredientName(new IngredientNameListener() {
//				@Override
//				public void onIngredientNameAvailable(String name, String ean) {
//					if(name == null) {
//						Toast.makeText(getApplicationContext(), "Error while getting the data from the server, please try later", Toast.LENGTH_LONG).show();
//						mSwipeLayout.setRefreshing(false);
//					} else {
//						ObjectItem obj = new ObjectItem(name, ean);
//						obj.bought = true;
//						mAdapter.addObject(obj);
//						mAdapter.notifyDataSetChanged();
//						mSwipeLayout.setRefreshing(false);
//						//doRefresh();
//					}
//
//				}
//			}, cleanedBarcode);

        }

    }

    private void doRefresh() {
        mSwipeLayout.setRefreshing(true);
        DataLoader dl = new DataLoader();
        dl.getShoppingList(new ShoppingListLoaderListener() {
            @Override
            public void onShoppingListAvailable(ObjectItem[] objectItemData) {
                if (objectItemData != null) {
                    mAdapter.data = objectItemData;
                    mSwipeLayout.setRefreshing(false);
                    mAdapter.notifyDataSetChanged();
                } else {
                    Toast.makeText(getApplicationContext(), "Error while getting the data from the server, please try later", Toast.LENGTH_LONG).show();
                    mSwipeLayout.setRefreshing(false);
                }
            }
        });

    }

}
